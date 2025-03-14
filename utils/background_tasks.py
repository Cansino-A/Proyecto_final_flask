from threading import Thread
from flask import current_app
from models import User
from .steam_api import fetch_and_store_games

def start_background_fetch(user_id):
    """Inicia la descarga de juegos en segundo plano."""
    def task_wrapper():
        with current_app.app_context():
            user = User.query.get(user_id)
            if user:
                try:
                    fetch_and_store_games(user)
                except Exception as e:
                    current_app.logger.error(f"Error en tarea en segundo plano: {str(e)}")

    thread = Thread(target=task_wrapper)
    thread.start()