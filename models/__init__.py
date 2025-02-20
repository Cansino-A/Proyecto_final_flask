from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Inicializa la extensión de la base de datos

# 🕹️ Modelo Game: representa un juego en la base de datos
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Identificador único
    title = db.Column(db.String(100), nullable=False)  # Título del juego (requerido)
    progress = db.Column(db.Float, nullable=False)  # Progreso del juego en porcentaje
    notes = db.Column(db.Text, nullable=True)  # Notas adicionales sobre el juego

    def __repr__(self):
        return f"<Game {self.title} - {self.progress}%>"  # Representación legible para depuración