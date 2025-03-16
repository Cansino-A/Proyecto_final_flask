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
            return {
                "champion": player_data.get("championName", "Desconocido"),
                "kills": player_data.get("kills", 0),
                "deaths": player_data.get("deaths", 0),
                "assists": player_data.get("assists", 0),
                "win": player_data.get("win", False),
                "duration": player_data.get("timePlayed", 0) // 60,  # Convertir a minutos
                "gameMode": player_data.get("gameMode", "Desconocido"),
                "totalDamageDealt": player_data.get("totalDamageDealt", 0),
                "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions", 0),
                "totalHeal": player_data.get("totalHeal", 0),
                "goldEarned": player_data.get("goldEarned", 0),
                "totalMinionsKilled": player_data.get("totalMinionsKilled", 0),
                "items": [player_data.get(f"item{i}", 0) for i in range(6)],  # Items comprados
                "summonerSpells": [
                    player_data.get("summoner1Id", 0),
                    player_data.get("summoner2Id", 0)
                ],  # Hechizos de invocador
                "runes": [
                    {
                        "name": rune.get("name", "Desconocido"),
                        "icon": rune.get("icon", "")
                    } for rune in player_data.get("perks", {}).get("styles", [])
                ]  # Runas
            }
        else:
            return {"error": "Jugador no encontrado en la partida"}, 404
    else:
        return {"error": response.json()}, response.status_code