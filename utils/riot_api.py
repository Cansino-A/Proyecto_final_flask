import requests
from flask import current_app

# 🔹 URLs base de Riot API
BASE_ACCOUNT_URL = "https://europe.api.riotgames.com"
BASE_MATCH_URL = "https://europe.api.riotgames.com"

def get_latest_version():
    """Obtiene la última versión de Data Dragon desde la API de Riot."""
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)
    if response.status_code == 200:
        versions = response.json()
        return versions[0]  # La primera versión es la más reciente
    return "13.24.1"  # Versión por defecto si falla la solicitud

def get_puuid(game_name, tag_line):
    """Obtiene el PUUID del jugador a partir de su Riot ID."""
    riot_api_key = current_app.config.get("RIOT_API_KEY")
    
    if not riot_api_key:
        return {"error": "API Key no encontrada"}, 401

    url = f"{BASE_ACCOUNT_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": riot_api_key}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get("puuid", "")
    else:
        return {"error": response.json()}, response.status_code

def get_match_history(puuid):
    """Obtiene el historial de partidas del jugador (últimas 5 partidas)."""
    riot_api_key = current_app.config.get("RIOT_API_KEY")

    if not riot_api_key:
        return {"error": "API Key no encontrada"}, 401

    url = f"{BASE_MATCH_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    headers = {"X-Riot-Token": riot_api_key}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}, response.status_code

def get_match_details(match_id, puuid):
    """Obtiene detalles de una partida específica."""
    riot_api_key = current_app.config.get("RIOT_API_KEY")

    if not riot_api_key:
        return {"error": "API Key no encontrada"}, 401

    url = f"{BASE_MATCH_URL}/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": riot_api_key}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()
        player_data = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
        
        if player_data:
            # Obtener la versión más reciente de Data Dragon para las imágenes
            version = get_latest_version()
            champion_image_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{player_data.get('championName', 'Unknown')}.png"
            
            # Obtener el queueId para identificar el tipo de partida
            queue_id = match_data["info"].get("queueId", 0)

            # Diccionario para traducir el queueId a un modo de juego
            queue_id_translation = {
                420: "Clasificatoria Solo/Duo",
                440: "Clasificatoria Flexible",
                400: "Normal (Draft Pick)",
                430: "Normal (Blind Pick)",
                450: "ARAM",
                900: "URF",
                1700: "Arena",
                1900: "Teamfight Tactics (Normal)",
                1100: "Teamfight Tactics (Clasificatoria)",
                # Puedes añadir más queueId según sea necesario
            }

            # Traducir el queueId
            translated_game_mode = queue_id_translation.get(queue_id, "Otro")

            # Estadísticas adicionales
            wards_placed = player_data.get("wardsPlaced", 0)
            wards_killed = player_data.get("wardsKilled", 0)
            dragons_killed = player_data.get("dragonKills", 0)
            barons_killed = player_data.get("baronKills", 0)
            champion_level = player_data.get("champLevel", 0)

            # Calcular el KDA Global
            kills = player_data.get("kills", 0)
            deaths = player_data.get("deaths", 1)  # Evitar división por cero
            assists = player_data.get("assists", 0)

            return {
                "champion": player_data.get("championName", "Desconocido"),
                "champion_image": champion_image_url,
                "kills": kills,
                "deaths": deaths,
                "assists": assists,
                "win": player_data.get("win", False),
                "duration": player_data.get("timePlayed", 0) // 60,  # Convertir a minutos
                "gameMode": translated_game_mode,  # Modo de juego traducido usando queueId
                "totalDamageDealt": player_data.get("totalDamageDealt", 0),
                "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions", 0),
                "totalHeal": player_data.get("totalHeal", 0),
                "goldEarned": player_data.get("goldEarned", 0),
                "totalMinionsKilled": player_data.get("totalMinionsKilled", 0),
                "gameStartTimestamp": match_data["info"].get("gameStartTimestamp", 0),  # Fecha de la partida
                "wardsPlaced": wards_placed,
                "wardsKilled": wards_killed,
                "dragonsKilled": dragons_killed,
                "baronsKilled": barons_killed,
                "championLevel": champion_level
            }
        else:
            return {"error": "Jugador no encontrado en la partida"}, 404
    else:
        return {"error": response.json()}, response.status_code


def get_summoner_info(puuid):
    """Obtiene información básica del invocador."""
    riot_api_key = current_app.config.get("RIOT_API_KEY")

    if not riot_api_key:
        return {"error": "API Key no encontrada"}, 401

    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    headers = {"X-Riot-Token": riot_api_key}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}, response.status_code

def get_ranked_info(summoner_id):
    """Obtiene la clasificación del invocador."""
    riot_api_key = current_app.config.get("RIOT_API_KEY")

    if not riot_api_key:
        return {"error": "API Key no encontrada"}, 401

    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": riot_api_key}
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}, response.status_code