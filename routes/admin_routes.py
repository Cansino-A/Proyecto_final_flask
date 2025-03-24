from flask import jsonify, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.achievement import Achievement
from utils.riot_api import get_ranked_info, get_puuid, get_summoner_info 
from forms.registration_form import RegistrationForm
from werkzeug.security import generate_password_hash

@login_required
def users():
    return render_template('users.html', current_user=current_user)

@login_required
def users_api():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    sort_by = request.args.get("sort", "username")
    order = request.args.get("order", "asc")

    # Consulta mejorada con conteo de logros
    query = db.session.query(
        User,
        db.func.count(Achievement.id).filter(Achievement.achieved == True).label('total_achievements')
    ).outerjoin(Achievement).group_by(User.id)

    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    # Ordenación segura
    order_column = {
        "username": User.username,
        "achievements": db.text('total_achievements')
    }.get(sort_by, User.username)

    query = query.order_by(order_column.asc() if order == "asc" else order_column.desc())

    paginated_users = query.paginate(page=page, per_page=10, error_out=False)
    
    users_data = [{
        "id": user.id,
        "username": user.username,
        "total_achievements": total_achievements,
        "highest_rank": "N/A"  # Implementar lógica de ranking si es necesario
    } for user, total_achievements in paginated_users.items]

    return jsonify({
        "users": users_data,
        "total_pages": paginated_users.pages,
        "current_page": page
    })



def get_highest_rank(user):
    """Obtiene el rango más alto de un usuario en League of Legends."""
    if not user.summoner_name or not user.riot_tag:
        return None
        
    try:
        puuid = get_puuid(user.summoner_name, user.riot_tag)
        if isinstance(puuid, dict) and "error" in puuid:
            return None
            
        summoner_info = get_summoner_info(puuid)
        if "error" in summoner_info:
            return None
            
        ranked_info = get_ranked_info(summoner_info["id"])
        if isinstance(ranked_info, dict) and "error" in ranked_info:
            return None
            
        if not isinstance(ranked_info, list) or len(ranked_info) == 0:
            return "Unranked"
            
        # Orden de los rangos de menor a mayor
        rank_order = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        
        # Encontrar el rango más alto
        highest_rank = max(
            ranked_info,
            key=lambda x: rank_order.index(x["tier"]) if x["tier"] in rank_order else -1
        )
        
        return f"{highest_rank['tier']} {highest_rank['rank']}"
    except Exception as e:
        print(f"Error getting rank for user {user.username}: {str(e)}")
        return None

@login_required
def update_delete_user(user_id):
    if current_user.username != "admin":
        return jsonify({"error": "Acceso denegado"}), 403

    user = User.query.get_or_404(user_id)

    if request.method == 'PUT':
        data = request.get_json()
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        if 'username' in data:
            user.username = data['username']
        db.session.commit()
        return jsonify({"success": True, "message": "Usuario actualizado"})

    elif request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "Usuario eliminado"})

    
@login_required
def create_user():
    if current_user.username != "admin":
        return jsonify({"error": "Acceso denegado"}), 403

    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Usuario ya existe"}), 400

    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": True, "message": "Usuario creado"})