from flask import render_template, redirect, url_for, flash, request, jsonify, get_flashed_messages, flash, current_app
from forms.login_form import LoginForm
from flask_login import login_required, current_user, login_user, logout_user
from models import db
from models.game import Game
from models.achievement import Achievement
from models.user import User
from utils.steam_api import fetch_steam_username
from utils.riot_api import get_puuid
from utils.background_tasks import start_background_fetch
from forms.registration_form import RegistrationForm
import random
import os


def register():
    """Maneja el registro de nuevos usuarios."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el nombre de usuario ya está registrado
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Este nombre de usuario ya está registrado.', 'warning')
            return redirect(url_for('register'))

        # Obtener lista de iconos disponibles
        icons_dir = os.path.join(current_app.root_path, 'static', 'images', 'icons')
        icons = [f for f in os.listdir(icons_dir) if f.startswith('icon') and f.endswith('.jpg')]
        
        # Asignar un icono aleatorio
        if icons:
            icon_id = random.randint(1, len(icons))  # Índice aleatorio basado en la cantidad de iconos
        else:
            icon_id = 1  # Valor por defecto si no hay iconos

        # Crear el nuevo usuario
        user = User(username=form.username.data, profile_icon_id=icon_id)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Iniciar sesión y redirigir
        login_user(user, remember=True)
        flash('Cuenta creada con éxito.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

def login():
    """Maneja el inicio de sesión de usuarios."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Iniciar sesión sin recordar por defecto
            login_user(user, remember=False)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html', form=form)

def logout():
    """Maneja el cierre de sesión de usuarios."""
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('index'))

@login_required
def profile():
    """Muestra la página de configuración del usuario."""
    # Obtener lista de iconos disponibles
    icons_dir = os.path.join(current_app.root_path, 'static', 'images', 'icons')
    icons = [f for f in os.listdir(icons_dir) if f.startswith('icon') and f.endswith('.jpg')]
    
    return render_template('profile.html', total_icons=len(icons))

@login_required
def update_username():
    """Actualiza el nombre de usuario."""
    new_username = request.json.get('username')
    if new_username:
        current_user.username = new_username
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "El nombre de usuario no puede estar vacío."}), 400


@login_required
def link_steam():
    """Vincula el Steam ID al usuario e inicia la descarga de juegos."""
    steam_id = request.json.get('steam_id')
    if steam_id:
        # Verificar si el Steam ID es válido
        steam_name = fetch_steam_username(steam_id, current_app.config['STEAM_API_KEY'])
        if not steam_name:
            return jsonify({"success": False, "error": "El ID de Steam no es válido o no existe."}), 400

        # Eliminar juegos antiguos asociados al usuario
        Game.query.filter_by(user_id=current_user.id).delete()
        Achievement.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()

        # Actualizar el Steam ID y nombre de Steam del usuario
        current_user.steam_id = steam_id
        current_user.steam_name = steam_name  # Añadir el nombre de Steam
        current_user.is_fetching = True
        current_user.progress = 0
        db.session.commit()

        # Iniciar la descarga de juegos en segundo plano
        start_background_fetch(current_user.id)
        flash('Steam ID vinculado correctamente. Descargando juegos...', 'success')
        return jsonify({
            "success": True,
            "steam_name": steam_name  # Devolver el nombre de Steam
        })
    else:
        return jsonify({"success": False, "error": "El ID de Steam no puede estar vacío."}), 400


@login_required
def update_riot_info():
    """Actualiza el nombre de invocador y el tag de Riot."""
    summoner_name = request.json.get('summoner_name')
    riot_tag = request.json.get('riot_tag')

    if summoner_name and riot_tag:
        # Verificar si el nombre de invocador y el tag son válidos
        puuid = get_puuid(summoner_name, riot_tag)
        if isinstance(puuid, dict) and "error" in puuid:
            return jsonify({"success": False, "error": "El nombre de invocador o el tag no son válidos."}), 400

        # Actualizar la información en la base de datos
        current_user.summoner_name = summoner_name
        current_user.riot_tag = riot_tag
        db.session.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Datos inválidos"}), 400
    
@login_required
def update_password():
    """Cambia la contraseña del usuario."""
    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')
    confirm_new_password = request.json.get('confirm_new_password')

    if not current_user.check_password(current_password):
        return jsonify({"success": False, "error": "La contraseña actual es incorrecta."}), 400

    if new_password != confirm_new_password:
        return jsonify({"success": False, "error": "Las nuevas contraseñas no coinciden."}), 400

    current_user.set_password(new_password)
    db.session.commit()
    return jsonify({"success": True})

@login_required
def change_profile_icon():
    try:
        icon_id = request.json.get('icon_id')
        print(f"[DEBUG] Icon ID recibido: {icon_id}")  # Depuración
        
        # Validar existencia de iconos
        icons_dir = os.path.join(current_app.root_path, 'static', 'images', 'icons')
        print(f"[DEBUG] Ruta de iconos: {icons_dir}")  # Depuración
        
        icons = [f for f in os.listdir(icons_dir) if f.startswith('icon') and f.endswith('.jpg')]
        print(f"[DEBUG] Iconos encontrados: {icons}")  # Depuración
        
        if 1 <= icon_id <= len(icons):
            current_user.profile_icon_id = icon_id
            db.session.commit()
            return jsonify({"success": True})
        else:
            print(f"[ERROR] ID de icono inválido: {icon_id}")  # Depuración
            return jsonify({"success": False, "error": "Invalid icon ID"}), 400
    except Exception as e:
        print(f"[ERROR] Excepción en change_profile_icon: {str(e)}")  # Depuración
        return jsonify({"success": False, "error": str(e)}), 500