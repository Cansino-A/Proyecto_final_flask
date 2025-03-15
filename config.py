import os
from datetime import timedelta

class Config:
    # Clave secreta para la aplicación Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui')

    # Configuración de la base de datos SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'games.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de la sesión
    SESSION_COOKIE_NAME = 'my_session'
    SESSION_PERMANENT = False
    REMEMBER_COOKIE_DURATION = timedelta(days=30)

    # Clave API de Steam
    STEAM_API_KEY = "C89BEF3321862C5B2AA16A35B9BFC5C0"