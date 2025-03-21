from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Regexp

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."),
        Length(min=4, max=25, message="El nombre de usuario debe tener entre 4 y 25 caracteres."),
        Regexp(r'^[a-zA-Z0-9_]+$', message="El nombre de usuario solo puede contener letras, números y guiones bajos.")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=1, message="La contraseña no puede estar vacía.")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message="Debes confirmar la contraseña."),
        EqualTo('password', message="Las contraseñas no coinciden.")
    ])
    submit = SubmitField('Registrar')