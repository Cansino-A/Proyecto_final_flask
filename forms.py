from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=25)])
    steam_id = StringField('Steam ID', validators=[DataRequired()])  # Campo steam_id agregado
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=9)])  # Longitud mínima de 6
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')