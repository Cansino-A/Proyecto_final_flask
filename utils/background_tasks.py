from threading import Thread
from flask import current_app
from models import db, User, Game
from utils.steam_api import fetch_and_store_steam_games

def fetch_steam_games(user):
    """Descarga y almacena juegos de Steam para un usuario."""
    try:
        if user.steam_id:
            steam_api_key = current_app.config.get('STEAM_API_KEY')
            if not steam_api_key:
                raise ValueError("STEAM_API_KEY no está configurada.")
            fetch_and_store_steam_games(user, steam_api_key)
    except Exception as e:
        current_app.logger.error(f"Error al descargar juegos de Steam: {str(e)}")
        raise

def update_user_progress(user, progress):
    """Actualiza el progreso del usuario."""
    user.progress = progress
    user.is_fetching = progress < 100
    db.session.commit()

def start_background_fetch(user_id):
    """Inicia la descarga de juegos en segundo plano."""
    def task_wrapper(app, user_id):
        with app.app_context():
            user = User.query.get(user_id)
            if user:
                try:
                    # Descargar juegos de Steam si hay un Steam ID vinculado
                    if user.steam_id:
                        fetch_steam_games(user)

                    # Actualizar el estado del usuario
                    update_user_progress(user, 100)
                except Exception as e:
                    current_app.logger.error(f"Error en el hilo: {str(e)}")
                    update_user_progress(user, 0)

    app = current_app._get_current_object()
    thread = Thread(target=task_wrapper, args=(app, user_id))
    thread.start()