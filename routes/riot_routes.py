from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.user import User
from config import Config
import requests
import json

riot_bp = Blueprint('riot', __name__)

# URLs base de Riot API
BASE_ACCOUNT_URL = "https://europe.api.riotgames.com"
BASE_MATCH_URL = "https://europe.api.riotgames.com"
BASE_SUMMONER_URL = "https://euw1.api.riotgames.com"

@riot_bp.route('/api/riot/user-stats')
@login_required
def get_user_stats():
    try:
        # Verificar si el usuario tiene una cuenta de Riot vinculada
        if not current_user.summoner_name or not current_user.riot_tag:
            return jsonify({
                "error": "No tienes una cuenta de Riot vinculada. Por favor, vincula tu cuenta en tu perfil."
            }), 400

        # Obtener el PUUID del jugador
        puuid_url = f"{BASE_ACCOUNT_URL}/riot/account/v1/accounts/by-riot-id/{current_user.summoner_name}/{current_user.riot_tag}"
        headers = {"X-Riot-Token": Config.RIOT_API_KEY}
        puuid_response = requests.get(puuid_url, headers=headers)
        
        if puuid_response.status_code != 200:
            return jsonify({
                "error": "No se pudo encontrar tu cuenta de Riot. Verifica que el nombre y el tag sean correctos."
            }), 400
            
        puuid_data = puuid_response.json()
        puuid = puuid_data.get('puuid')
        
        if not puuid:
            return jsonify({
                "error": "No se encontró el PUUID de tu cuenta de Riot."
            }), 400

        # Obtener el historial de partidas
        matches_url = f"{BASE_MATCH_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        matches_response = requests.get(matches_url, headers=headers)
        
        if matches_response.status_code != 200:
            return jsonify({
                "error": "Error al obtener el historial de partidas."
            }), 400
            
        matches = matches_response.json()[:10]  # Obtener las últimas 10 partidas

        return jsonify({
            "puuid": puuid,
            "matches": matches
        })

    except Exception as e:
        print(f"Error en get_user_stats: {str(e)}")  # Para debugging
        return jsonify({
            "error": "Error al obtener las estadísticas del usuario."
        }), 500

@riot_bp.route('/api/riot/summoner-info')
@login_required
def get_summoner_info():
    puuid = request.args.get('puuid')
    
    if not puuid:
        return jsonify({"error": "Se requiere el PUUID del jugador"}), 400

    try:
        headers = {"X-Riot-Token": Config.RIOT_API_KEY}
        
        # Obtener información del invocador
        summoner_url = f"{BASE_SUMMONER_URL}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        summoner_response = requests.get(summoner_url, headers=headers)
        
        if summoner_response.status_code != 200:
            return jsonify({"error": "Error al obtener información del invocador"}), 400
            
        summoner_data = summoner_response.json()
        summoner_id = summoner_data.get('id')
        
        if not summoner_id:
            return jsonify({"error": "No se encontró el ID del invocador"}), 400

        # Obtener información de clasificación
        ranked_url = f"{BASE_SUMMONER_URL}/lol/league/v4/entries/by-summoner/{summoner_id}"
        ranked_response = requests.get(ranked_url, headers=headers)
        
        if ranked_response.status_code != 200:
            return jsonify({"error": "Error al obtener información de clasificación"}), 400
            
        ranked_info = ranked_response.json()

        return jsonify({
            "rankedInfo": ranked_info
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@riot_bp.route('/api/riot/match/<match_id>')
@login_required
def get_match_details(match_id):
    puuid = request.args.get('puuid')
    
    if not puuid:
        return jsonify({"error": "Se requiere el PUUID del jugador"}), 400

    try:
        headers = {"X-Riot-Token": Config.RIOT_API_KEY}
        
        # Obtener detalles de la partida
        match_url = f"{BASE_MATCH_URL}/lol/match/v5/matches/{match_id}"
        match_response = requests.get(match_url, headers=headers)
        
        if match_response.status_code != 200:
            return jsonify({"error": "Error al obtener detalles de la partida"}), 400
            
        match_data = match_response.json()
        
        # Verificar que la respuesta tenga la estructura esperada
        if "info" not in match_data or "participants" not in match_data["info"]:
            return jsonify({"error": "Formato de datos de partida inválido"}), 500
            
        player_data = next((p for p in match_data["info"]["participants"] if p["puuid"] == puuid), None)
        
        if not player_data:
            return jsonify({"error": "Jugador no encontrado en la partida"}), 404

        # Formatear los datos para el frontend
        return jsonify({
            "win": player_data.get("win", False),
            "champion": player_data.get("championName", "Unknown"),
            "champion_image": f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/{player_data.get('championName', 'Unknown')}.png",
            "kills": player_data.get("kills", 0),
            "deaths": player_data.get("deaths", 0),
            "assists": player_data.get("assists", 0),
            "gameMode": match_data["info"].get("gameMode", "Unknown"),
            "gameStartTimestamp": match_data["info"].get("gameCreation", 0),
            "duration": match_data["info"].get("gameDuration", 0) // 60,  # Convertir a minutos
            "championLevel": player_data.get("champLevel", 1),
            "totalDamageDealt": player_data.get("totalDamageDealt", 0),
            "totalDamageDealtToChampions": player_data.get("totalDamageDealtToChampions", 0),
            "totalHeal": player_data.get("totalHeal", 0),
            "goldEarned": player_data.get("goldEarned", 0),
            "totalMinionsKilled": player_data.get("totalMinionsKilled", 0),
            "wardsPlaced": player_data.get("wardsPlaced", 0),
            "wardsKilled": player_data.get("wardsKilled", 0),
            "dragonsKilled": player_data.get("dragonsKilled", 0),
            "baronsKilled": player_data.get("baronsKilled", 0)
        })

    except Exception as e:
        print(f"Error en get_match_details: {str(e)}")  # Para debugging
        return jsonify({"error": f"Error al procesar los detalles de la partida: {str(e)}"}), 500

@riot_bp.route('/api/riot/summoner')
@login_required
def get_summoner():
    game_name = request.args.get('gameName')
    tag_line = request.args.get('tagLine')
    
    if not game_name or not tag_line:
        return jsonify({"error": "Se requiere gameName y tagLine"}), 400

    try:
        # Obtener el PUUID del jugador
        puuid_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        headers = {"X-Riot-Token": Config.RIOT_API_KEY}
        puuid_response = requests.get(puuid_url, headers=headers)
        
        if puuid_response.status_code != 200:
            return jsonify({"error": "Jugador no encontrado"}), 404
            
        puuid_data = puuid_response.json()
        puuid = puuid_data.get('puuid')
        
        if not puuid:
            return jsonify({"error": "No se encontró el PUUID del jugador"}), 404

        # Obtener el historial de partidas
        matches_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        matches_response = requests.get(matches_url, headers=headers)
        
        if matches_response.status_code != 200:
            return jsonify({"error": "Error al obtener el historial de partidas"}), 400
            
        matches = matches_response.json()[:10]  # Obtener las últimas 10 partidas

        return jsonify({
            "puuid": puuid,
            "matches": matches
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500 