from . import db

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)  # Referencia a 'game.id'
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    achieved = db.Column(db.Boolean, default=False)

    game = db.relationship('Game', backref=db.backref('achievements', lazy=True))