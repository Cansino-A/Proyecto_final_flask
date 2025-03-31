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
    """API para gestionar usuarios."""
    if request.method == 'GET':
        try:
            page = request.args.get('page', 1, type=int)
            search = request.args.get('search', '')
            sort_by = request.args.get('sort', 'username')
            order = request.args.get('order', 'asc')

            # Consulta base para obtener todos los usuarios excepto admin
            query = User.query.filter(User.username != 'admin')

            if search:
                query = query.filter(User.username.ilike(f'%{search}%'))

            if sort_by == 'username':
                query = query.order_by(User.username.asc() if order == 'asc' else User.username.desc())
            elif sort_by == 'achievements':
                query = query.order_by(User.total_achievements.asc() if order == 'asc' else User.total_achievements.desc())
            elif sort_by == 'rank':
                query = query.order_by(User.highest_rank.asc() if order == 'asc' else User.highest_rank.desc())

            pagination = query.paginate(page=page, per_page=10, error_out=False)
            users = pagination.items

            # Lista para almacenar los datos de usuarios procesados
            processed_users = []

            # Procesar cada usuario
            for user in users:
                try:
                    # Actualizar rango si tiene información de Riot
                    if user.summoner_name and user.riot_tag:
                        try:
                            user.highest_rank = get_highest_rank(user)
                        except Exception as e:
                            print(f"Error al obtener rango para usuario {user.username}: {str(e)}")
                            user.highest_rank = "Error al obtener rango"
                    
                    # Actualizar total de logros
                    try:
                        user.total_achievements = Achievement.query.filter_by(user_id=user.id, achieved=True).count()
                    except Exception as e:
                        print(f"Error al obtener logros para usuario {user.username}: {str(e)}")
                        user.total_achievements = 0

                    # Agregar usuario procesado a la lista
                    processed_users.append({
                        'id': user.id,
                        'username': user.username,
                        'highest_rank': user.highest_rank or 'N/A',
                        'total_achievements': user.total_achievements or 0,
                        'steam_name': user.steam_name or 'No vinculado',
                        'riot_info': f"{user.summoner_name}#{user.riot_tag}" if user.summoner_name and user.riot_tag else 'No vinculado'
                    })
                except Exception as e:
                    print(f"Error procesando usuario {user.username}: {str(e)}")
                    # Si hay error al procesar un usuario, agregarlo con valores por defecto
                    processed_users.append({
                        'id': user.id,
                        'username': user.username,
                        'highest_rank': 'N/A',
                        'total_achievements': 0,
                        'steam_name': 'No vinculado',
                        'riot_info': 'No vinculado'
                    })

            try:
                db.session.commit()
            except Exception as e:
                print(f"Error al guardar cambios en la base de datos: {str(e)}")
                db.session.rollback()

            return jsonify({
                'users': processed_users,
                'total_pages': pagination.pages,
                'current_page': page
            })
        except Exception as e:
            print(f"Error en users_api: {str(e)}")
            return jsonify({'error': 'Error al cargar usuarios'}), 500

    elif request.method == 'POST':
        if current_user.username != "admin":
            return jsonify({'success': False, 'error': 'No tienes permisos para crear usuarios'}), 403

        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Se requiere nombre de usuario y contraseña'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'El nombre de usuario ya existe'}), 400

        try:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Usuario creado correctamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

@login_required
def update_delete_user(user_id):
    """API para actualizar o eliminar usuarios."""
    if current_user.username != "admin":
        return jsonify({'success': False, 'error': 'No tienes permisos para realizar esta acción'}), 403

    user = User.query.get_or_404(user_id)
    
    # Evitar que se elimine el usuario admin
    if user.username == 'admin':
        return jsonify({'error': 'No se puede eliminar el usuario administrador'}), 403
        
    if request.method == 'PUT':
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')

        try:
            if new_username:
                user.username = new_username
            if new_password:
                user.set_password(new_password)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Usuario eliminado correctamente'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

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
            return "Sin rango"
            
        # Diccionario de traducción de rangos
        rank_translations = {
            "IRON": "Hierro",
            "BRONZE": "Bronce",
            "SILVER": "Plata",
            "GOLD": "Oro",
            "PLATINUM": "Platino",
            "DIAMOND": "Diamante",
            "MASTER": "Maestro",
            "GRANDMASTER": "Gran Maestro",
            "CHALLENGER": "Desafiante"
        }
        
        # Orden de los rangos de menor a mayor
        rank_order = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        
        # Encontrar el rango más alto
        highest_rank = max(
            ranked_info,
            key=lambda x: rank_order.index(x["tier"]) if x["tier"] in rank_order else -1
        )
        
        return f"{rank_translations.get(highest_rank['tier'], highest_rank['tier'])} {highest_rank['rank']}"
    except Exception as e:
        print(f"Error getting rank for user {user.username}: {str(e)}")
        return None