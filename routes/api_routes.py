from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.game import Game
from models.achievement import Achievement
from utils.riot_api import get_puuid, get_match_history, get_match_details




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