from flask import render_template, jsonify, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from models import db
from models.game import Game
from models.achievement import Achievement
from utils.steam_api import fetch_steam_username  # Importar fetch_steam_username

@login_required
def dashboard():
    """Muestra el dashboard con los juegos del usuario."""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Obtener el nombre de Steam del usuario
    steam_name = fetch_steam_username(current_user.steam_id, current_app.config['STEAM_API_KEY'])

    # Calcular el número total de logros obtenidos
    total_achievements = Achievement.query.filter_by(user_id=current_user.id, achieved=True).count()

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Número de juegos por página
        games_query = Game.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
        games = [
            {
                "id": game.id,
                "name": game.name,
                "playtime": game.playtime,
                "image": game.image,
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
            "current_page": page,
            "total_achievements": total_achievements  # Incluir el número total de logros obtenidos
        })

    # Si no es una solicitud AJAX, renderizar el template
    return render_template('dashboard.html', 
                           user_id=current_user.id, 
                           steam_name=steam_name, 
                           total_achievements=total_achievements)

def loading(user_id):
    """Muestra la pantalla de carga mientras se descargan los juegos."""
    return render_template('loading.html', user_id=user_id)