from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Importa db desde __init__.py

class User(db.Model, UserMixin):
    __tablename__ = 'user'  # Especifica el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    steam_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)