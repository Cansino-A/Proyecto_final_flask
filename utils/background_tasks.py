from threading import Thread
from flask import current_app
from models import db, User
from utils.steam_api import fetch_and_store_games


def start_background_fetch(user_id):
    """Inicia la descarga de juegos en segundo plano."""
    def task_wrapper(app, user_id):
        # Crear un nuevo contexto de aplicación para el hilo
        with app.app_context():
            user = User.query.get(user_id)
            if user:
                try:
                    # Obtener la clave de la API de Steam desde la configuración
                    steam_api_key = current_app.config.get('STEAM_API_KEY')
                    if not steam_api_key:
                        raise ValueError("STEAM_API_KEY no está configurada.")
                    
                    # Llamar a la función con ambos argumentos
                    fetch_and_store_games(user, steam_api_key)
                except Exception as e:
                    current_app.logger.error(f"Error en el hilo: {str(e)}")
                    # Actualizar el estado del usuario en caso de error
                    user.progress = 0
                    user.is_fetching = False
                    db.session.commit()

    # Obtener la aplicación Flask actual
    app = current_app._get_current_object()  # Esto evita problemas con el proxy de Flask
    thread = Thread(target=task_wrapper, args=(app, user_id))
    thread.start()