from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, NumberRange

# 📝 Formulario para agregar un nuevo juego
class GameForm(FlaskForm):
    title = StringField('Título del juego', validators=[InputRequired(message="El título es obligatorio.")])
    progress = DecimalField('Progreso (%)', validators=[
        InputRequired(message="El progreso es obligatorio."),
        NumberRange(min=0, max=100, message="El progreso debe estar entre 0 y 100.")
    ])
    notes = TextAreaField('Notas')  # Campo opcional para notas
    submit = SubmitField('Guardar')  # Botón de envío