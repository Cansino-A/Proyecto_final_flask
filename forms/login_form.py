from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Regexp

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Regexp(r'^[a-zA-Z0-9_]+$', message="El nombre de usuario solo puede contener letras, números y guiones bajos")])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')