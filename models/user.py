from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    steam_id = db.Column(db.String(50), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0)
    is_fetching = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} (ID: {self.id})>"