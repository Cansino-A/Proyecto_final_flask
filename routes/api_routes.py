from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.game import Game
from models.achievement import Achievement
from utils.riot_api import get_puuid, get_match_history, get_match_details, get_summoner_info, get_ranked_info




def api_games():
    """API para obtener los juegos del usuario."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Usuario no autenticado"}), 401

    page = request.args.get('page', 1, type=int)
    per_page = 10
    games_query = Game.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    games = [
        {
            "id": game.id,
            "appid": game.appid,
            "name": game.name,
            "playtime": game.playtime,
            "image": game.image,
            "platform": game.platform,  # Añadir la plataforma
            "achieved_achievements": [
                {
                    "name": a.name,
                    "description": a.description,
                    "unlock_time": a.unlock_time.strftime("%Y-%m-%d %H:%M:%S") if a.unlock_time else None
                } for a in Achievement.query.filter_by(game_id=game.id, achieved=True).all()
            ],
            "pending_achievements": [
                {
                    "name": a.name,
                    "description": a.description
                } for a in Achievement.query.filter_by(game_id=game.id, achieved=False).all()
            ]
        } for game in games_query.items
    ]

    return jsonify({
        "games": games,
        "total_pages": games_query.pages,
        "current_page": page
    })

def get_achievements(appid):
    """API para obtener los logros de un juego específico."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Usuario no autenticado"}), 401

    game = Game.query.filter_by(appid=appid, user_id=current_user.id).first_or_404()
    achievements = Achievement.query.filter_by(game_id=game.id, user_id=current_user.id).all()

    achievements_data = [{
        'name': a.name,
        'description': a.description,
        'achieved': a.achieved,
        'unlock_time': a.unlock_time.strftime("%Y-%m-%d %H:%M:%S") if a.unlock_time else None
    } for a in achievements]

    return jsonify({'achievements': achievements_data})

@login_required
def check_games_status():
    """API para verificar el estado de la descarga de juegos."""
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "Se requiere un user_id"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verifica si hay juegos en la base de datos para este usuario
    if Game.query.filter_by(user_id=user.id).first():
        return jsonify({"status": "done", "progress": 100})  # La descarga ha terminado
    else:
        return jsonify({"status": "loading", "progress": user.progress if hasattr(user, 'progress') else 0})  # La descarga aún está en progreso
    
@login_required
def check_download_status():
    """API para verificar el estado de la descarga."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Usuario no autenticado"}), 401

    user = User.query.get(current_user.id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Verificar si la descarga está completa
    download_complete = user.progress == 100

    return jsonify({
        "download_complete": download_complete,
        "progress": user.progress
    })

@login_required
def total_achievements():
    """API para obtener el número total de logros obtenidos."""
    try:
        total_achievements = Achievement.query.filter_by(user_id=current_user.id, achieved=True).count()
        return jsonify({
            "success": True,
            "total_achievements": total_achievements
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })
    
@login_required     
def riot_summoner():
    """ Obtiene el historial de partidas de un jugador """
    game_name = request.args.get("gameName")
    tag_line = request.args.get("tagLine")

    if not game_name or not tag_line:
        return jsonify({"error": "Se requiere gameName y tagLine"}), 400

    puuid = get_puuid(game_name, tag_line)
    if isinstance(puuid, dict):  # Error en la respuesta
        return jsonify(puuid), 400

    match_history = get_match_history(puuid)
    return jsonify({"puuid": puuid, "matches": match_history})

@login_required   
def riot_match_details(match_id):
    """ Obtiene detalles de una partida específica """
    puuid = request.args.get("puuid")

    if not puuid:
        return jsonify({"error": "Se requiere el PUUID"}), 400

    match_details = get_match_details(match_id, puuid)
    return jsonify(match_details)

@login_required
def summoner_info():
    """Obtiene información básica del invocador."""
    puuid = request.args.get("puuid")
    if not puuid:
        return jsonify({"error": "Se requiere el PUUID"}), 400

    try:
        # Obtener información básica del invocador
        summoner_info = get_summoner_info(puuid)
        if "error" in summoner_info:
            return jsonify(summoner_info), 400

        # Obtener información de clasificación
        ranked_info = get_ranked_info(summoner_info["id"])
        if "error" in ranked_info:
            ranked_info = "No clasificado"

        # Imprimir la respuesta para depuración
        print("Respuesta de summoner_info:", summoner_info)
        print("Respuesta de ranked_info:", ranked_info)

        return jsonify({
            "summonerLevel": summoner_info.get("summonerLevel", "Desconocido"),
            "rankedInfo": ranked_info
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@login_required
def user_stats():
    """Obtiene las estadísticas detalladas del usuario de Steam."""
    if not current_user.steam_id:
        return jsonify({"error": "No hay cuenta de Steam vinculada"}), 404

    try:
        # Obtener todos los juegos del usuario
        games = Game.query.filter_by(user_id=current_user.id, platform='Steam').all()
        
        # Calcular estadísticas generales
        total_games = len(games)
        total_playtime = sum(game.playtime for game in games)
        
        # Calcular logros totales (corregido para todos los juegos)
        total_achievements = Achievement.query.filter_by(user_id=current_user.id, achieved=True).count()
        total_possible_achievements = Achievement.query.filter_by(user_id=current_user.id).count()
        
        # Obtener juegos más jugados (top 5)
        most_played_games = sorted(games, key=lambda x: x.playtime, reverse=True)[:5]
        
        # Agrupar juegos por género (simulado)
        genres = {
            "Acción": 0,
            "Aventura": 0,
            "RPG": 0,
            "Estrategia": 0,
            "Deportes": 0,
            "Otros": 0
        }
        
        # Simular distribución de géneros
        for game in games:
            if game.playtime > 0:
                genres["Acción"] += game.playtime * 0.3
                genres["Aventura"] += game.playtime * 0.2
                genres["RPG"] += game.playtime * 0.2
                genres["Estrategia"] += game.playtime * 0.15
                genres["Deportes"] += game.playtime * 0.1
                genres["Otros"] += game.playtime * 0.05
        
        # Obtener actividad reciente (últimos 7 días)
        recent_activity = []
        for game in games:
            # Usar la fecha de última vez jugado como timestamp
            timestamp = int(game.last_played.timestamp()) if game.last_played else 0
            recent_activity.append({
                "timestamp": timestamp,
                "playtime": game.playtime
            })
        
        # Ordenar actividad por fecha
        recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Preparar lista de juegos recientes
        recent_games = []
        for game in games:
            # Obtener logros específicos para este juego
            game_achievements = Achievement.query.filter_by(game_id=game.id).all()
            achieved_count = sum(1 for a in game_achievements if a.achieved)
            total_game_achievements = len(game_achievements)
            
            # Calcular fecha de última vez jugado
            last_played = None
            if game.last_played:
                last_played = int(game.last_played.timestamp())
            
            recent_games.append({
                "name": game.name,
                "header_image": game.image,
                "playtime": game.playtime,
                "last_played": last_played,
                "achievements": achieved_count,
                "total_achievements": total_game_achievements
            })
        
        # Ordenar juegos recientes por última vez jugado
        recent_games.sort(key=lambda x: x["last_played"] or 0, reverse=True)
        
        return jsonify({
            "totalGames": total_games,
            "totalPlaytime": total_playtime,
            "totalAchievements": total_achievements,
            "totalPossibleAchievements": total_possible_achievements,
            "mostPlayedGames": [
                {
                    "name": game.name,
                    "playtime": game.playtime
                } for game in most_played_games
            ],
            "timeByGenre": [
                {
                    "name": genre,
                    "playtime": playtime
                } for genre, playtime in genres.items()
            ],
            "completedGames": len([game for game in games if game.playtime > 0]),
            "favoriteGenres": ["Acción", "Aventura", "RPG"],  # Simulado
            "lastPlayedGame": most_played_games[0].name if most_played_games else "Ninguno",
            "personaState": "En línea",  # Simulado
            "username": current_user.steam_name if hasattr(current_user, 'steam_name') else "Usuario de Steam"  # Usar el nombre de Steam
        })
    except Exception as e:
        print(f"Error en user_stats: {str(e)}")  # Añadir log para depuración
        return jsonify({"error": str(e)}), 500