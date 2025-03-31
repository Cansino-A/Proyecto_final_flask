import requests
from datetime import datetime
from models import db, Game, Achievement
from flask import current_app

def fetch_steam_username(steam_id, steam_api_key):
    """Obtiene el nombre de usuario de Steam desde su API."""
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steam_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("response", {}).get("players"):
            return data["response"]["players"][0]["personaname"]
    return None

def fetch_steam_game_name(appid):
    """Obtiene el nombre de un juego desde la API de Steam."""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if str(appid) in data and data[str(appid)]["success"]:
            return data[str(appid)]["data"]["name"]
    return "Unknown Game"

def fetch_steam_achievement_names(appid):
    """Obtiene los nombres legibles de los logros desde la API de Steam."""
    try:
        url = f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={current_app.config['STEAM_API_KEY']}&appid={appid}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "game" in data and "availableGameStats" in data["game"]:
                achievements = data["game"]["availableGameStats"]["achievements"]
                if achievements:  # Verificar si hay logros
                    return {ach["name"]: ach["displayName"] for ach in achievements}
                else:
                    current_app.logger.info(f"El juego {appid} no tiene logros.")
            else:
                current_app.logger.error(f"No se encontraron logros para el juego {appid}.")
        else:
            current_app.logger.error(f"Error al obtener logros para el juego {appid}: {response.status_code}")
        return {}
    except Exception as e:
        current_app.logger.error(f"Error en fetch_steam_achievement_names para el juego {appid}: {str(e)}")
        return {}

def fetch_and_store_steam_games(user, steam_api_key):
    """Descarga y almacena juegos de Steam para un usuario."""
    try:
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={steam_api_key}&steamid={user.steam_id}"
        response = requests.get(url)

        if response.status_code == 200 and "games" in response.json().get("response", {}):
            games_data = response.json()["response"]["games"]
            _process_steam_games(user, games_data)

            # Actualizar el estado de la descarga
            user.progress = 100
            user.last_updated = datetime.utcnow()
            db.session.commit()
    except Exception as e:
        user.progress = 0
        user.is_fetching = False
        db.session.commit()

def _process_steam_games(user, games_data):
    """Procesa la lista de juegos y los almacena en la base de datos."""
    total_games = len(games_data)
    for index, game in enumerate(games_data):
        existing_game = Game.query.filter_by(appid=game["appid"], user_id=user.id).first()
        
        if not existing_game:
            # Obtener el nombre del juego
            game_name = fetch_steam_game_name(game["appid"])

            new_game = Game(
                appid=game["appid"],
                name=game_name,
                playtime=game.get("playtime_forever", 0) // 60,
                image=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['appid']}/capsule_184x69.jpg",
                platform='Steam',
                user_id=user.id,
                last_played=datetime.utcnow()  # Establecer la fecha de última vez jugado
            )
            db.session.add(new_game)
        else:
            # Actualizar el juego existente
            existing_game.playtime = game.get("playtime_forever", 0) // 60
            existing_game.last_played = datetime.utcnow()  # Actualizar la fecha de última vez jugado
        
        db.session.commit()

        # Intentar obtener logros para todos los juegos
        try:
            _fetch_steam_achievements(user, game["appid"])
        except Exception as e:
            current_app.logger.error(f"Error al obtener logros para el juego {game_name} (ID: {game['appid']}): {str(e)}")
        
        # Actualizar progreso
        user.progress = int((index + 1) / total_games * 100)
        db.session.commit()

    user.last_updated = datetime.utcnow()
    user.progress = 100
    db.session.commit()

def _fetch_steam_achievements(user, appid):
    """Obtiene y almacena logros para un juego específico."""
    try:
        # Obtener los nombres legibles de los logros
        achievement_names = fetch_steam_achievement_names(appid)
        
        # Obtener los logros del usuario
        url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={current_app.config['STEAM_API_KEY']}&steamid={user.steam_id}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "playerstats" in data and "achievements" in data["playerstats"]:
                achievements_data = data["playerstats"]["achievements"]
                if achievements_data:  # Verificar si hay logros
                    _process_steam_achievements(user, appid, achievements_data, achievement_names)
    except Exception as e:
        current_app.logger.error(f"Error en _fetch_steam_achievements para el juego {appid}: {str(e)}")

def _process_steam_achievements(user, appid, achievements_data, achievement_names):
    """Procesa y almacena logros en la base de datos."""
    game = Game.query.filter_by(appid=appid, user_id=user.id).first()
    if not game:
        return

    for ach in achievements_data:
        display_name = achievement_names.get(ach["apiname"], ach["apiname"])
        
        achievement = Achievement.query.filter_by(
            game_id=game.id, 
            user_id=user.id, 
            name=display_name  # Usar el nombre legible en lugar del apiname
        ).first()

        if not achievement:
            new_achievement = Achievement(
                game_id=game.id,
                user_id=user.id,
                name=display_name,
                description="Unlocked" if ach["achieved"] else "Locked",
                achieved=bool(ach["achieved"]),
                unlock_time=datetime.utcfromtimestamp(ach["unlocktime"]) if ach.get("unlocktime") else None
            )
            db.session.add(new_achievement)
        else:
            achievement.achieved = bool(ach["achieved"])
            achievement.unlock_time = datetime.utcfromtimestamp(ach["unlocktime"]) if ach.get("unlocktime") else None
    
    db.session.commit()