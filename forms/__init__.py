from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

# 📌 Formulario de registro
class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=25)])
    steam_id = StringField('Steam ID', validators=[DataRequired()])  # Campo steam_id agregado
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=5)])  # Longitud mínima de 6
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

# 🔑 Formulario de inicio de sesión
class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')
