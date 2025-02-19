'''
# * FLASK: CONFIGURACIÓN E INTRODUCCIÓN 🚀
# ======================================================
# ? Este archivo explica cómo instalar y entender la estructura del proyecto Flask.

# * 1️⃣ INSTALACIÓN DEL PROYECTO
# ------------------------------------------------------
# ? Para comenzar con este proyecto, sigue estos pasos:

# ✅ Paso 1: Clona el repositorio desde GitHub Classroom 
# ✅ Paso 2: Descomprime `Proyecto_final_flask.zip` en una carpeta de tu elección.
# ✅ Paso 3: Abre una terminal en la carpeta del proyecto y ejecuta:
# 
# ```sh
# pip install -r requirements.txt
# ```
# ? Esto instalará Flask y todas las dependencias necesarias.
# 
# ✅ Paso 3: Para ejecutar el servidor Flask, usa:
# 
# ```sh
# python app.py
# ```
# ? Luego, abre en tu navegador: `http://127.0.0.1:5000/`


# * 2️⃣ ¿QUÉ ES FLASK?
# ------------------------------------------------------
# ? Flask es un microframework para Python que permite crear aplicaciones web de manera rápida y sencilla.
# 
# 🔹 Ligero y fácil de aprender.
# 🔹 Soporte para enrutamiento de URLs.
# 🔹 Integración con bases de datos mediante SQLAlchemy.
# 🔹 Compatible con plantillas HTML mediante Jinja2.
# 🔹 Extensible con múltiples librerías.


# * 3️⃣ ESTRUCTURA DEL PROYECTO
# ------------------------------------------------------
# ? Este proyecto sigue la siguiente estructura:
#
# 📂 `flask_project/`
# ├── 🟢 `app.py`             # * Archivo principal que inicia el servidor Flask
# ├── 🔵 `config.py`          # * Configuraciones generales del proyecto
# ├── 🟡 `requirements.txt`   # * Dependencias necesarias
# │
# ├── 🟠 `templates/`         # * Archivos HTML (Frontend)
# │   ├── 🔹 `base.html`      # ? Plantilla base para todas las páginas
# │   ├── 🔹 `index.html`     # ? Página principal (Aquí se coloca el código Bootstrap)
# │
# ├── 🟣 `static/`            # * Archivos estáticos (CSS, JS, imágenes)
# │   ├── 🎨 `css/style.css`  # ? Archivo CSS para los estilos
# │   ├── 💻 `js/script.js`   # ? Archivo JS para interacciones en el cliente
# │
# ├── 🚏 `routes/`            # * Carpeta para organizar rutas Flask
# │   ├── 🔹 `__init__.py`    # ? Archivo necesario para que Python reconozca el módulo
# │
# ├── 📊 `models/`            # * Carpeta para modelos de base de datos
# │   ├── 🔹 `__init__.py`    # ? Inicializa la base de datos
# │
# ├── 📋 `forms/`             # * Carpeta para manejar formularios Flask-WTF
# │   ├── 🔹 `__init__.py`    # ? Configuración de formularios


# * 4️⃣ DÓNDE AGREGAR BOOTSTRAP
# ------------------------------------------------------
# ? Para usar Bootstrap en el proyecto, se debe incluir en `templates/base.html` o `templates/index.html`:
#
# ```html
# <head>
#     <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
# </head>
# ```
# ? Esto permitirá usar clases de Bootstrap para dar estilos a la web.


# * 5️⃣ DÓNDE AÑADIR EL BACKEND
# ------------------------------------------------------
# ? Las funcionalidades del backend deben agregarse en `routes/` y en `models/`.
#
# 🔹 Ejemplo de cómo definir una ruta en `app.py`:
# ```python
# from flask import Flask, render_template
#
# app = Flask(__name__)
#
# @app.route('/')
# def home():
#     return render_template('index.html')
#
# if __name__ == '__main__':
#     app.run(debug=True)
# ```
# ? Para manejar bases de datos, se deben definir modelos en `models/` y configurar en `config.py`.


# 🚀 *¡LISTO PARA PROGRAMAR!* 🚀
# ------------------------------------------------------
# ✅ Cada estudiante puede empezar modificando `index.html`, agregando rutas en `app.py` y creando modelos para bases de datos.
# 🎯 ¡A programar!
'''
