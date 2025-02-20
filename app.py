import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Game
from flask_sqlalchemy import SQLAlchemy
from forms import GameForm
from models import db, Game

# 📝 Configuración de la aplicación Flask y la base de datos
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)  # Vincula la base de datos a la app

# 🔑 Reemplaza con tu API Key de Steam
STEAM_API_KEY = "C89BEF3321862C5B2AA16A35B9BFC5C0"

# 🏠 Ruta principal: muestra la lista de juegos registrados
@app.route('/')
def index():
    games = Game.query.all()  # Consulta todos los juegos de la base de datos
    return render_template('index.html', games=games)  # Renderiza la plantilla con la lista de juegos

# ➕ Ruta para agregar un nuevo juego con un formulario
@app.route('/add', methods=['GET', 'POST'])
def add_game():
    form = GameForm()
    if form.validate_on_submit():  # Verifica que el formulario se haya enviado correctamente
        new_game = Game(
            title=form.title.data,
            progress=form.progress.data or 0,  # Asegura que si es None se guarde como 0
            notes=form.notes.data
        )
        db.session.add(new_game)  # Agrega el juego a la base de datos
        db.session.commit()  # Guarda los cambios
        flash('¡Juego agregado con éxito!', 'success')  # Mensaje de confirmación
        return redirect(url_for('index'))  # Redirige a la página principal
    return render_template('add_game.html', form=form)  # Muestra el formulario de agregar juego

# 📄 Ruta para ver los detalles de un juego específico
@app.route('/game/<int:game_id>')
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)  # Obtiene el juego por ID o muestra un error 404
    return render_template('game_detail.html', game=game)  # Renderiza la página de detalles

# 🗑️ Ruta para eliminar un juego (colócala antes del if __name__ == '__main__')
@app.route('/delete/<int:game_id>', methods=['POST'])
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)  # Busca el juego o lanza un 404 si no existe
    db.session.delete(game)  # Elimina el juego
    db.session.commit()  # Guarda los cambios
    flash(f'Juego \"{game.title}\" eliminado con éxito.', 'success')  # Mensaje de éxito
    return redirect(url_for('index'))  # Redirige a la lista de juegos

# 🏆 Ruta para consultar logros de un juego en Steam
@app.route('/steam/logros', methods=['GET', 'POST'])
def logros_steam():
    achievements = None
    if request.method == 'POST':
        steam_id = request.form.get('steam_id')
        app_id = request.form.get('app_id')

        if not steam_id or not app_id:
            flash('Debes proporcionar el Steam ID y el App ID del juego.', 'warning')
            return redirect(url_for('logros_steam'))

        # 📥 Petición a la API de Steam
        url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={STEAM_API_KEY}&steamid={steam_id}&appid={app_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "playerstats" in data and "achievements" in data["playerstats"]:
                achievements = data["playerstats"]["achievements"]
                flash('Logros obtenidos correctamente.', 'success')
            else:
                flash('No se encontraron logros para este usuario o juego.', 'danger')
        else:
            flash('Error al consultar la API de Steam.', 'danger')

    return render_template('logros_steam.html', achievements=achievements)

# 🚀 Ejecuta la app y crea la base de datos
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
    app.run(debug=True)  # Inicia el servidor
