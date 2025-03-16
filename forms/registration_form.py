from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=25), Regexp(r'^[a-zA-Z0-9_]+$', message="El nombre de usuario solo puede contener letras, números y guiones bajos")])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=1)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')