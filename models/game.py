from . import db

class Game(db.Model):
    __tablename__ = 'game'  # Nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.Integer, nullable=False)  # ID del juego en Steam
    name = db.Column(db.String(255), nullable=False)
    playtime = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # Referencia a 'user.id'

    # Relación con User
    user = db.relationship('User', backref=db.backref('games', lazy=True))

    # Relación con Achievement
    achievements = db.relationship('Achievement', backref='game', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Game {self.name} (ID: {self.id}, AppID: {self.appid})>"