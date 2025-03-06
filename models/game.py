from . import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appid = db.Column(db.Integer, nullable=False)  # ID del juego en Steam
    name = db.Column(db.String(255), nullable=False)
    playtime = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # Referencia a 'user.id'

    user = db.relationship('User', backref=db.backref('games', lazy=True))