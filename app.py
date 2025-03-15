from flask import Flask, render_template
from flask_login import LoginManager
from flask_socketio import SocketIO
from models import db
from models.user import User
from routes.auth_routes import register, login, logout
from routes.game_routes import dashboard, loading
from routes.api_routes import api_games, get_achievements, check_games_status, check_download_status, total_achievements
from utils.background_tasks import start_background_fetch



# Configuración de Flask
app = Flask(__name__)
app.config.from_object('config.Config')
socketio = SocketIO(app)

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

# Registrar rutas de juegos
app.route('/dashboard')(dashboard)
app.route('/loading/<int:user_id>')(loading)

# Registrar rutas de la API
app.route('/api/games')(api_games)
app.route('/api/achievements/<int:appid>')(get_achievements)
app.route('/api/check_games_status')(check_games_status)  
app.route('/api/check_download_status')(check_download_status)
app.route('/api/total_achievements')(total_achievements) 

# Crear la base de datos al iniciar la aplicación
with app.app_context():
    db.create_all()
    print("✅ Base de datos creada correctamente.")

if __name__ == '__main__':
    socketio.run(app, debug=True)