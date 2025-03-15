from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from models import db
from models.user import User
from utils.steam_api import fetch_steam_username
from utils.background_tasks import start_background_fetch
from forms.registration_form import RegistrationForm
from forms.login_form import LoginForm
from flask import current_app  # Importar current_app

def register():
    """Maneja el registro de nuevos usuarios."""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el nombre de usuario ya está registrado
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Este nombre de usuario ya está registrado.', 'warning')
            return redirect(url_for('register'))

        # Verificar si el Steam ID ya está registrado
        existing_steam_user = User.query.filter_by(steam_id=form.steam_id.data).first()
        if existing_steam_user:
            flash('Este Steam ID ya está registrado.', 'warning')
            return redirect(url_for('register'))

        try:
            # Obtener el nombre de Steam (solo para verificar que el Steam ID es válido)
            steam_name = fetch_steam_username(form.steam_id.data, current_app.config['STEAM_API_KEY'])
            if not steam_name:
                flash('No se pudo obtener el nombre de Steam. Verifica tu ID de Steam.', 'danger')
                return redirect(url_for('register'))
        except Exception as e:
            flash('Error al conectar con la API de Steam. Inténtalo de nuevo más tarde.', 'danger')
            return redirect(url_for('register'))

        # Crear el nuevo usuario con el nombre de usuario ingresado
        user = User(username=form.username.data, steam_id=form.steam_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Iniciar sesión y redirigir
        login_user(user, remember=True)
        flash('Cuenta creada con éxito. Redirigiendo a tu biblioteca...', 'success')

        # Iniciar la descarga de juegos en segundo plano
        start_background_fetch(user.id)

        # Redirigir directamente al dashboard
        return redirect(url_for('dashboard'))

    return render_template('register.html', form=form)

def login():
    """Maneja el inicio de sesión de usuarios."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        flash('Steam ID o contraseña incorrectos.', 'danger')
    return render_template('login.html', form=form)

def logout():
    """Maneja el cierre de sesión de usuarios."""
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))