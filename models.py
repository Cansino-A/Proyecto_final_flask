from app import db

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    progress = db.Column(db.Integer, nullable=False)  # Porcentaje de avance
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<Game {self.title} - {self.progress}%>"