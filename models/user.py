from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    steam_id = db.Column(db.String(50), unique=True)
    steam_name = db.Column(db.String(100))
    summoner_name = db.Column(db.String(50))
    riot_tag = db.Column(db.String(10))
    password_hash = db.Column(db.String(120), nullable=False)
    profile_icon_id = db.Column(db.Integer, default=1)
    last_updated = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0)
    is_fetching = db.Column(db.Boolean, default=False)
    highest_rank = db.Column(db.String(50))
    total_achievements = db.Column(db.Integer, default=0)

    @property
    def is_admin(self):
        return self.username == "admin"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} (ID: {self.id})>"