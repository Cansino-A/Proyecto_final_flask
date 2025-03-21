from flask import jsonify, request, render_template
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.achievement import Achievement
from utils.riot_api import get_ranked_info

# Ruta para renderizar la página HTML
@login_required
def users():
    return render_template("users.html")

# Ruta para la API (devuelve JSON)
@login_required
def users_api():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    sort_by = request.args.get("sort", "username")
    order = request.args.get("order", "asc")

    query = User.query

    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    # ... (resto de la lógica para ordenar)

    users = query.paginate(page=page, per_page=10, error_out=False)

    users_data = []
    for user in users.items:
        users_data.append({
            "id": user.id,
            "username": user.username,
            "total_achievements": Achievement.query.filter_by(user_id=user.id, achieved=True).count(),
            "highest_rank": "Unranked"  # Valor temporal
        })

    return jsonify({
        "users": users_data,
        "total_pages": users.pages,
        "current_page": page
    })

def get_highest_rank(user):
    # Implementar lógica para obtener el rango más alto de LoL
    pass

def update_user(user):
    # Implementar lógica para editar un usuario
    pass 

def delete_user(user):
    # Implementar lógica para eliminar un usuario
    pass