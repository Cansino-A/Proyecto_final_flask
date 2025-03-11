from . import db

class Achievement(db.Model):
    __tablename__ = 'achievement'  # Nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id', ondelete='CASCADE'), nullable=False)  # Clave foránea a Game
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)  # Clave foránea a User
    name = db.Column(db.String(255), nullable=False)  # Nombre del logro
    description = db.Column(db.String(512), nullable=True)  # Descripción del logro
    achieved = db.Column(db.Boolean, default=False)  # ¿Está conseguido?
    unlock_time = db.Column(db.DateTime, nullable=True)  # Fecha de desbloqueo

    def __repr__(self):
        return f"<Achievement {self.name} (ID: {self.id}, Game ID: {self.game_id})>"