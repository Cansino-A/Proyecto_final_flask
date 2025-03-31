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
    SESSION_PERMANENT = False  # La sesión no será permanente
    REMEMBER_COOKIE_DURATION = timedelta(days=0)  # La cookie de "recordar" durará 0 días
    SESSION_COOKIE_SECURE = True  # Solo enviar la cookie por HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevenir acceso a la cookie por JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # Protección contra CSRF

    # Clave API de Steam
    STEAM_API_KEY = "C89BEF3321862C5B2AA16A35B9BFC5C0"
    RIOT_API_KEY = "RGAPI-5da79d3f-36c1-4eb2-a841-f4e3c3c4829e" #Hay que cambiarla cada 24 horas Expires: Sun, Mar 16th, 2025 @ 4:37pm (PT)
