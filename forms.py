from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class GameForm(FlaskForm):
    title = StringField('Título del juego', validators=[DataRequired(message="El título es obligatorio.")])
    progress = IntegerField('Progreso (%)', validators=[
        NumberRange(min=-1, max=100, message="El progreso debe estar entre 0 y 100.")
    ])
    notes = TextAreaField('Notas')
    submit = SubmitField('Guardar')
