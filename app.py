from flask import Flask, render_template
from flask_login import LoginManager
from flask_socketio import SocketIO
from models import db
from models.user import User
from routes.auth_routes import register, login, logout, profile, update_username, update_password, link_steam, update_riot_info, change_profile_icon
from routes.game_routes import dashboard, dashboard_steam, dashboard_riot, stats_riot, stats_steam
from routes.api_routes import api_games, get_achievements, check_games_status, check_download_status, total_achievements, riot_summoner, riot_match_details, summoner_info, user_stats
from routes.riot_routes import riot_bp
from utils.background_tasks import start_background_fetch
from routes.admin_routes import users, users_api, update_delete_user
import logging
import os

# Configuración de Flask
app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)
logging.basicConfig(level=logging.ERROR)

# Inicializar la base de datos
db.init_app(app)

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Registrar rutas de autenticación
app.route('/register', methods=['GET', 'POST'])(register)
app.route('/login', methods=['GET', 'POST'])(login)
app.route('/logout')(logout)
app.route('/profile', methods=['GET', 'POST'])(profile)
app.route('/update_username', methods=['POST'])(update_username)
app.route('/update_password', methods=['POST'])(update_password)
app.route('/link_steam', methods=['POST'])(link_steam)
app.route('/update_riot_info', methods=['POST'])(update_riot_info)
app.route('/change_profile_icon', methods=['POST'])(change_profile_icon)

# Registrar rutas de juegos
app.route('/dashboard')(dashboard)
app.route('/dashboard/steam')(dashboard_steam)
app.route('/dashboard/riot')(dashboard_riot)
app.route('/stats/riot')(stats_riot)
app.route('/stats/steam')(stats_steam)

# Registrar rutas de Steam
app.route('/api/games')(api_games)
app.route('/api/achievements/<int:appid>')(get_achievements)
app.route('/api/check_games_status')(check_games_status)  
app.route('/api/check_download_status')(check_download_status)
app.route('/api/total_achievements')(total_achievements)
app.route('/api/steam/user-stats')(user_stats)

# Registrar rutas de Riot
app.register_blueprint(riot_bp)

# Registrar rutas de administrador
app.route('/users')(users)
app.route('/api/users', methods=['GET', 'POST'])(users_api)
app.route('/api/users/<int:user_id>', methods=['PUT', 'DELETE'])(update_delete_user)

def init_db():
    """Inicializa la base de datos y crea el usuario admin si no existe."""
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Base de datos creada correctamente.")
        
        # Crear usuario admin si no existe
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                profile_icon_id=1,
                steam_name=None,
                summoner_name=None,
                riot_tag=None,
                highest_rank=None,
                total_achievements=0
            )
            admin.set_password("admin")
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado correctamente.")
        else:
            print("✅ Usuario admin ya existe.")

# Crear la base de datos al iniciar la aplicación
init_db()

if __name__ == '__main__':
    socketio.run(app, debug=True)