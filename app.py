import requests
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import db
from models.user import User
from models.game import Game
from models.achievement import Achievement
from forms import RegistrationForm, LoginForm
import os

# 🔑 Clave API de Steam (REEMPLAZA POR TU CLAVE REAL)
STEAM_API_KEY = "C89BEF3321862C5B2AA16A35B9BFC5C0"

# 📌 Configuración de Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'  # Agrega esta línea
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Inicializa la base de datos
db.init_app(app)

# 🔐 Configuración del LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🚀 FUNCIONES PARA CARGAR JUEGOS Y LOGROS
def fetch_and_store_games(user):
    """Descarga y almacena los juegos de un usuario de Steam."""
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={STEAM_API_KEY}&steamid={user.steam_id}&include_appinfo=true&include_played_free_games=true"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "response" in data and "games" in data["response"]:
            for game in data["response"]["games"]:
                existing_game = Game.query.filter_by(appid=game["appid"], user_id=user.id).first()

                if not existing_game:
                    new_game = Game(
                        appid=game["appid"],
                        name=game.get("name", "Juego Desconocido"),
                        playtime=game.get("playtime_forever", 0) // 60,
                        image=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['appid']}/capsule_184x69.jpg",
                        user_id=user.id
                    )
                    db.session.add(new_game)
                    db.session.commit()
                    fetch_and_store_achievements(new_game, user)

    user.last_updated = datetime.utcnow()
    db.session.commit()

def fetch_and_store_achievements(game, user):
    """Descarga y almacena los logros de un juego de Steam."""
    achievements_url = f"https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/?key={STEAM_API_KEY}&steamid={user.steam_id}&appid={game.appid}"
    achievements_response = requests.get(achievements_url)

    if achievements_response.status_code == 200:
        achievements_data = achievements_response.json()
        if "playerstats" in achievements_data and "achievements" in achievements_data["playerstats"]:
            for ach in achievements_data["playerstats"]["achievements"]:
                existing_achievement = Achievement.query.filter_by(game_id=game.id, name=ach.get("name")).first()
                
                if not existing_achievement:
                    achievement = Achievement(
                        game_id=game.id,
                        name=ach.get("name", "Logro Desconocido"),
                        description=ach.get("description", "Sin descripción"),
                        achieved=ach.get("achieved", 0) == 1
                    )
                    db.session.add(achievement)
    db.session.commit()

# 🌍 RUTAS DE LA APLICACIÓN
@app.route('/')
def index():
    return redirect(url_for('login'))  # Redirige a la página de inicio de sesión

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verifica si el usuario ya existe
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'warning')
            return redirect(url_for('register'))

        # Crea un nuevo usuario
        user = User(username=form.username.data, steam_id=form.steam_id.data)
        user.set_password(form.password.data)  # 🔑 Encripta la contraseña
        db.session.add(user)
        db.session.commit()

        fetch_and_store_games(user)  # 🔄 Descargar juegos y logros al registrar

        flash('Cuenta creada con éxito. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    else:
        # Muestra errores en el formulario
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en el campo {field}: {error}", 'danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            print(f"Usuario encontrado: {user.username}")  # Depuración
            if user.check_password(form.password.data):
                print("Contraseña correcta")  # Depuración
                login_user(user)
                flash('Inicio de sesión exitoso.', 'success')
                return redirect(url_for('dashboard'))
            else:
                print("Contraseña incorrecta")  # Depuración
                flash('Usuario o contraseña incorrectos.', 'danger')
        else:
            print("Usuario no encontrado")  # Depuración
            flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Muestra el dashboard y actualiza los juegos/logros si es necesario."""
    if current_user.last_updated is None or (datetime.utcnow() - current_user.last_updated) > timedelta(hours=24):
        fetch_and_store_games(current_user)  # 🔄 Actualizar si pasaron más de 24 horas

    games = Game.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', games=games)

# 📂 API PARA CARGA ASINCRÓNICA DE JUEGOS Y LOGROS
@app.route('/api/games')
@login_required
def api_games():
    """API para obtener juegos paginados."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    games_query = Game.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)

    games = [
        {
            "appid": game.appid,
            "name": game.name,
            "playtime": game.playtime,
            "image": game.image,
            "achieved_count": Achievement.query.filter_by(game_id=game.id, achieved=True).count()
        } for game in games_query.items
    ]

    return jsonify({
        "games": games,
        "total_pages": games_query.pages,
        "current_page": page
    })

@app.route('/api/achievements/<int:appid>')
@login_required
def api_achievements(appid):
    """API para obtener logros de un juego específico."""
    game = Game.query.filter_by(appid=appid, user_id=current_user.id).first()
    if not game:
        return jsonify({"error": "Juego no encontrado"}), 404

    achievements = Achievement.query.filter_by(game_id=game.id, achieved=True).all()

    return jsonify({
        "achievements": [
            {"name": ach.name, "description": ach.description} for ach in achievements
        ]
    })

# 🚀 EJECUTAR APP Y CREAR BD
with app.app_context():
    db.create_all()  # 🔥 Aquí se crean las tablas
    print("✅ Base de datos creada correctamente.")

if __name__ == '__main__':
    app.run(debug=True)
