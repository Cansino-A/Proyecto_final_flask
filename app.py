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
    """Descarga y almacena los juegos de un usuario de Steam, evitando duplicados."""
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={STEAM_API_KEY}&steamid={user.steam_id}&include_appinfo=true&include_played_free_games=true"
    
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "response" in data and "games" in data["response"]:
            print(f"🎮 Juegos encontrados: {len(data['response']['games'])}")

            for game in data["response"]["games"]:
                existing_game = Game.query.filter_by(appid=game["appid"], user_id=user.id).first()

                if existing_game:
                    print(f"🔸 Juego ya existe en la BD: {existing_game.name} (ID: {existing_game.appid})")
                    continue  # 🚨 Si ya existe, pasa al siguiente juego

                print(f"✅ Agregando juego a la BD: {game.get('name', 'Juego Desconocido')} (ID: {game['appid']})")
                
                new_game = Game(
                    appid=game["appid"],
                    name=game.get("name", "Juego Desconocido"),
                    playtime=game.get("playtime_forever", 0) // 60,
                    image=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game['appid']}/capsule_184x69.jpg",
                    user_id=user.id
                )

                db.session.add(new_game)
                db.session.commit()  # 🔥 Guarda el juego inmediatamente para evitar duplicados

                fetch_and_store_achievements(user, new_game.appid)  # ⬅ Llamar a logros solo para juegos nuevos

    user.last_updated = datetime.utcnow()
    db.session.commit()





def fetch_and_store_achievements(user, game_id):
    url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={game_id}&key={STEAM_API_KEY}&steamid={user.steam_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"⚠ Error obteniendo logros para {game_id}: {response.status_code}")
        return
    
    data = response.json()

    if "playerstats" in data and "achievements" in data["playerstats"]:
        print(f"✅ Logros obtenidos para {game_id}: {len(data['playerstats']['achievements'])}")
        
        # Obtener el juego de la base de datos usando el appid
        game = Game.query.filter_by(appid=game_id, user_id=user.id).first()
        if not game:
            print(f"⚠ Juego con appid {game_id} no encontrado en la base de datos.")
            return
        
        for achievement in data["playerstats"]["achievements"]:
            # Verificar si el logro ya existe en la base de datos
            existing_achievement = Achievement.query.filter_by(
                game_id=game.id,  # Usar el id del juego, no el appid
                user_id=user.id,
                name=achievement["apiname"]
            ).first()
            
            if not existing_achievement:
                # Insertar el logro, independientemente de si está conseguido o no
                new_achievement = Achievement(
                    game_id=game.id,  # Usar el id del juego, no el appid
                    user_id=user.id,
                    name=achievement.get("displayName", achievement["apiname"]),  # Usar el nombre descriptivo si está disponible
                    description="Desbloqueado" if achievement["achieved"] else "Pendiente",
                    achieved=bool(achievement["achieved"]),  # Convertir a booleano
                    unlock_time=datetime.utcfromtimestamp(achievement["unlocktime"]) if achievement["unlocktime"] else None
                )
                db.session.add(new_achievement)
            else:
                # Actualizar el logro si ya existe
                existing_achievement.achieved = bool(achievement["achieved"])
                existing_achievement.unlock_time = datetime.utcfromtimestamp(achievement["unlocktime"]) if achievement["unlocktime"] else None
        
        db.session.commit()
    else:
        print(f"⚠ El juego {game_id} no tiene logros o no se pueden obtener.")




# 🌍 RUTAS DE LA APLICACIÓN
@app.route('/')
def index():
    return redirect(url_for('login'))

from threading import Thread

from flask_login import login_user

from flask_login import login_user

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El nombre de usuario ya está en uso.', 'warning')
            return redirect(url_for('register'))

        user = User(username=form.username.data, steam_id=form.steam_id.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=True)  # 🔥 Mantener la sesión activa

        flash('Cuenta creada con éxito. Redirigiendo a tu biblioteca...', 'success')

        # 🔥🚨 Evitar múltiples llamadas a la API Steam
        if not Game.query.filter_by(user_id=user.id).first():
            fetch_and_store_games(user)

        return redirect(url_for('loading', user_id=user.id)) 

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
    """Muestra el dashboard con los juegos paginados."""
    
    # Obtener la página actual (por defecto, página 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Mostrar 10 juegos por página

    # Obtener los juegos del usuario paginados
    games_pagination = Game.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    games = games_pagination.items

    # Asociar todos los logros a cada juego (obtenidos y pendientes)
    for game in games:
        game.achieved_achievements = Achievement.query.filter_by(game_id=game.id, achieved=True).all()
        game.pending_achievements = Achievement.query.filter_by(game_id=game.id, achieved=False).all()

    return render_template('dashboard.html', games=games, pagination=games_pagination)



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
def get_achievements(appid):
    user_id = current_user.id
    game = Game.query.filter_by(appid=appid, user_id=user_id).first_or_404()
    achievements = Achievement.query.filter_by(game_id=game.id, user_id=user_id).all()

    achievements_data = [{
        'name': a.name,
        'description': a.description,
        'achieved': a.achieved,
        'unlock_time': a.unlock_time.strftime("%Y-%m-%d %H:%M:%S") if a.unlock_time else 'No especificado'
    } for a in achievements]

    return jsonify({'achievements': achievements})



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

    # ✅ Si ya hay juegos en la BD, informar al frontend
    if Game.query.filter_by(user_id=user.id).first():
        return jsonify({"message": "Los juegos ya están en la base de datos.", "status": "done"})

    def fetch_data():
        with app.app_context():
            fetch_and_store_games(user)

    thread = Thread(target=fetch_data)
    thread.start()

    return jsonify({"success": True, "status": "loading"})  # 🚨 Indicar al frontend que sigue cargando






# 🚀 EJECUTAR APP Y CREAR BD
with app.app_context():
    db.create_all()
    print("✅ Base de datos creada correctamente.")

if __name__ == '__main__':
    app.run(debug=True)
