from flask_sqlalchemy import SQLAlchemy

# Inicializa SQLAlchemy
db = SQLAlchemy()

# Importa los modelos después de inicializar `db`
from .user import User
from .game import Game
from .achievement import Achievement