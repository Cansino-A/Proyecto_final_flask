import requests
from datetime import datetime
from flask import app  
from models import db, Game, Achievement

def fetch_steam_username(steam_id):
    """Obtiene el nombre de usuario de Steam desde su API."""
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={app.config['STEAM_API_KEY']}&steamids={steam_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("response", {}).get("players"):
            return data["response"]["players"][0]["personaname"]
    return None

def fetch_and_store_games(user):
    """Descarga y almacena juegos de Steam para un usuario."""
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={app.config['STEAM_API_KEY']}&steamid={user.steam_id}"
    response = requests.get(url)

    if response.status_code == 200 and "games" in response.json().get("response", {}):
        games_data = response.json()["response"]["games"]
        _process_games(user, games_data)

def _process_games(user, games_data):
    """Procesa la lista de juegos y los almacena en la base de datos."""
    total_games = len(games_data)
    for index, game in enumerate(games_data):
        if not Game.query.filter_by(appid=game["appid"], user_id=user.id).first():
            new_game = Game(
                appid=game["appid"],
                name=game.get("name", "Unknown Game"),
                playtime=game.get("playtime_forever", 0) // 60,
                image=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['appid']}/capsule_184x69.jpg",
                user_id=user.id
            )
            db.session.add(new_game)
            db.session.commit()
            _fetch_achievements(user, game["appid"])
            
            # Actualizar progreso
            user.progress = int((index + 1) / total_games * 100)
            db.session.commit()

    user.last_updated = datetime.utcnow()
    user.progress = 100
    db.session.commit()

def _fetch_achievements(user, appid):
    """Obtiene y almacena logros para un juego específico."""
    url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={app.config['STEAM_API_KEY']}&steamid={user.steam_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        achievements_data = response.json().get("playerstats", {}).get("achievements", [])
        _process_achievements(user, appid, achievements_data)

def _process_achievements(user, appid, achievements_data):
    """Procesa y almacena logros en la base de datos."""
    game = Game.query.filter_by(appid=appid, user_id=user.id).first()
    if not game:
        return

    for ach in achievements_data:
        achievement = Achievement.query.filter_by(
            game_id=game.id, 
            user_id=user.id, 
            name=ach["apiname"]
        ).first()

        if not achievement:
            new_achievement = Achievement(
                game_id=game.id,
                user_id=user.id,
                name=ach.get("displayName", ach["apiname"]),
                description="Unlocked" if ach["achieved"] else "Locked",
                achieved=bool(ach["achieved"]),
                unlock_time=datetime.utcfromtimestamp(ach["unlocktime"]) if ach.get("unlocktime") else None
            )
            db.session.add(new_achievement)
        else:
            achievement.achieved = bool(ach["achieved"])
            achievement.unlock_time = datetime.utcfromtimestamp(ach["unlocktime"]) if ach.get("unlocktime") else None
    
    db.session.commit()