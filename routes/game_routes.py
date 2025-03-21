from flask import render_template, jsonify, redirect, url_for, request, current_app
from flask_login import login_required, current_user
from models import db
from models.game import Game
from models.achievement import Achievement
from utils.steam_api import fetch_steam_username  

@login_required
def dashboard():
    """Muestra el dashboard general con todos los juegos."""
    steam_games = []

    if current_user.steam_id:
        steam_games = Game.query.filter_by(user_id=current_user.id, platform='Steam').all()

    return render_template('dashboard.html', steam_games=steam_games)

@login_required
def dashboard_steam():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    steam_name = fetch_steam_username(current_user.steam_id, current_app.config['STEAM_API_KEY'])
    total_achievements = Achievement.query.filter_by(user_id=current_user.id, achieved=True).count()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'name')
        order = request.args.get('order', 'asc')

        base_query = Game.query.filter_by(user_id=current_user.id, platform='Steam')

        if search:
            base_query = base_query.filter(Game.name.ilike(f'%{search}%'))

        if sort_by == 'name':
            order_by = Game.name.asc() if order == 'asc' else Game.name.desc()
        elif sort_by == 'playtime':
            order_by = Game.playtime.asc() if order == 'asc' else Game.playtime.desc()
        elif sort_by == 'achievements':
            from sqlalchemy import func, select
            achievements_subquery = select(
                Achievement.game_id,
                func.count(Achievement.id).filter(Achievement.achieved == True).label('total_achieved')
                ).group_by(Achievement.game_id).subquery()
            
            base_query = base_query.outerjoin(
                achievements_subquery,
                Game.id == achievements_subquery.c.game_id
            )
            order_by = func.coalesce(achievements_subquery.c.total_achieved, 0)
            order_by = order_by.asc() if order == 'asc' else order_by.desc()

        games_query = base_query.order_by(order_by).paginate(page=page, per_page=10, error_out=False)

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
            "total_achievements": total_achievements
        })

    return render_template('dashboard_steam.html', 
                           user_id=current_user.id, 
                           steam_name=steam_name, 
                           total_achievements=total_achievements)

@login_required
def dashboard_riot():
    return render_template("dashboard_riot.html")
