from flask import render_template, redirect, url_for, flash, request, jsonify, get_flashed_messages
from forms.login_form import LoginForm
from flask_login import login_required, current_user, login_user, logout_user
from models import db
from models.user import User
from utils.steam_api import fetch_steam_username
from utils.background_tasks import start_background_fetch
from forms.registration_form import RegistrationForm

def register():
    """Maneja el registro de nuevos usuarios."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el nombre de usuario ya está registrado
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Este nombre de usuario ya está registrado.', 'warning')
            return redirect(url_for('register'))

        # Crear el nuevo usuario sin Steam ID
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Iniciar sesión y redirigir
        login_user(user, remember=True)
        flash('Cuenta creada con éxito.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

from flask import flash

def login():
    """Maneja el inicio de sesión de usuarios."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
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
def configuration():
    """Muestra la página de configuración del usuario."""
    return render_template('config.html')

@login_required
def update_username():
    """Actualiza el nombre de usuario."""
    new_username = request.form.get('username')
    if new_username:
        current_user.username = new_username
        db.session.commit()
        flash('Nombre de usuario actualizado correctamente.', 'success')
    else:
        flash('El nombre de usuario no puede estar vacío.', 'danger')
    return redirect(url_for('configuration'))

@login_required
def update_password():
    """Actualiza la contraseña del usuario."""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    if not current_user.check_password(current_password):
        flash('La contraseña actual es incorrecta.', 'danger')
    elif new_password != confirm_new_password:
        flash('Las contraseñas no coinciden.', 'danger')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Contraseña actualizada correctamente.', 'success')
    return redirect(url_for('configuration'))

@login_required
def link_steam():
    """Vincula el Steam ID al usuario e inicia la descarga de juegos."""
    steam_id = request.form.get('steam_id')
    if steam_id:
        # Verificar que el Steam ID sea válido (debe ser un número)
        if not steam_id.isdigit():
            flash('El Steam ID debe ser un número.', 'danger')
            return redirect(url_for('configuration'))

        current_user.steam_id = steam_id
        current_user.is_fetching = True  # Marcar que se está descargando
        db.session.commit()

        # Iniciar la descarga de juegos en segundo plano
        start_background_fetch(current_user.id)

        flash('Steam ID vinculado correctamente. Descargando juegos...', 'success')
    else:
        flash('El Steam ID no puede estar vacío.', 'danger')
    return redirect(url_for('configuration'))