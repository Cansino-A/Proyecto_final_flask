import requests
import threading
import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_socketio import SocketIO
from datetime import datetime, timedelta
from models import db
from models.user import User
from models.game import Game
from models.achievement import Achievement
from forms import RegistrationForm, LoginForm

# 🔑 Clave API de Steam
STEAM_API_KEY = "C89BEF3321862C5B2AA16A35B9BFC5C0"

# 📌 Configuración de Flask
app = Flask(__name__)
socketio = SocketIO(app)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_NAME'] = 'my_session'
app.config['SESSION_PERMANENT'] = False
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)


# Inicializa la base de datos
db.init_app(app)

# 🔐 Configuración del LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🚀 FUNCIONES PARA CARGAR JUEGOS Y LOGROS EN SEGUNDO PLANO
def fetch_and_store_games(user):
    """Descarga y almacena los juegos de un usuario de Steam."""
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={STEAM_API_KEY}&steamid={user.steam_id}&include_appinfo=true&include_played_free_games=true"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "response" in data and "games" in data["response"]:
            print(f"🎮 Juegos encontrados: {len(data['response']['games'])}")

            for game in data["response"]["games"]:
                existing_game = Game.query.filter_by(appid=game["appid"], user_id=user.id).first()

                if not existing_game:
                    print(f"✅ Agregando juego a la BD: {game.get('name', 'Juego Desconocido')} (ID: {game['appid']})")
                    
                    new_game = Game(
                        appid=game["appid"],
                        name=game.get("name", "Juego Desconocido"),
                        playtime=game.get("playtime_forever", 0) // 60,
                        image=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['appid']}/capsule_184x69.jpg",
                        user_id=user.id
                    )

                    db.session.add(new_game)
                else:
                    print(f"🔸 Juego ya existe en la BD: {existing_game.name} (ID: {existing_game.appid})")

            db.session.commit()
            print("📥 Juegos guardados en la base de datos.")

    user.last_updated = datetime.utcnow()
    db.session.commit()


def fetch_and_store_achievements(game, user):
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
    return redirect(url_for('login'))

from threading import Thread

from flask_login import login_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'warning')
            return redirect(url_for('register'))

        # Crear nuevo usuario
        user = User(username=form.username.data, steam_id=form.steam_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # 🔥 Iniciar sesión automáticamente después de registrarse
        login_user(user, remember=True)  # ⬅ Esto evita que la sesión se pierda

        flash('Cuenta creada con éxito. Redirigiendo a tu biblioteca...', 'success')
        return redirect(url_for('loading', user_id=user.id))  # Redirigir a la pantalla de carga

    return render_template('register.html', form=form)





@app.route('/loading/<int:user_id>')
def loading(user_id):
    """Muestra la pantalla de carga y comienza a obtener juegos."""
    return render_template('loading.html', user_id=user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    """Muestra el dashboard y verifica si hay juegos almacenados en la BD."""
    games = Game.query.filter_by(user_id=current_user.id).all()

    if not games:
        print("🚨 No hay juegos en la base de datos para este usuario.")
    else:
        print(f"✅ Se encontraron {len(games)} juegos en la BD para {current_user.username}")
        for game in games:
            print(f" - {game.name} (ID: {game.appid})")

    return render_template('dashboard.html', games=games)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

from flask import jsonify, request
from flask_login import current_user

@app.route('/api/games')
def api_games():
    """API para obtener juegos paginados."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Usuario no autenticado"}), 401  # ⬅ Evita la redirección al login

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
    game = Game.query.filter_by(appid=appid, user_id=current_user.id).first()
    if not game:
        return jsonify({"error": "Juego no encontrado"}), 404
    achievements = Achievement.query.filter_by(game_id=game.id, achieved=True).all()
    return jsonify({"achievements": [{"name": a.name, "description": a.description} for a in achievements]})

@app.route('/check_games')
def check_games():
    games = Game.query.all()
    if not games:
        return "🚨 No hay juegos en la base de datos."
    return jsonify([{"appid": game.appid, "name": game.name} for game in games])

from threading import Thread

@app.route('/api/fetch_games')
def fetch_games():
    """API para iniciar la descarga de juegos en segundo plano."""
    user_id = request.args.get("user_id", type=int)
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    def fetch_data():
        with app.app_context():  # 👈 Asegura el contexto de la app
            fetch_and_store_games(user)

    thread = Thread(target=fetch_data)
    thread.start()

    return jsonify({"success": True})



# 🚀 EJECUTAR APP Y CREAR BD
with app.app_context():
    db.create_all()
    print("✅ Base de datos creada correctamente.")

if __name__ == '__main__':
    app.run(debug=True)
