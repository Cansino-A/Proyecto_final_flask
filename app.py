import os
from flask import Flask, render_template  # Añadir render_template
from flask_login import LoginManager
from models import db
from models.user import User
from routes.auth_routes import register, login, logout

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'games.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Configurar Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Registrar rutas de autenticación
app.route('/register', methods=['GET', 'POST'])(register)
app.route('/login', methods=['GET', 'POST'])(login)
app.route('/logout')(logout)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crear todas las tablas
        print("✅ Base de datos y tablas creadas correctamente.")
    app.run(debug=True)