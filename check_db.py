from models import db, User, Game, Achievement
from app import app

# Ejecutar dentro del contexto de la aplicación
with app.app_context():
    print("🔄 Eliminando y recreando la base de datos...")
    db.drop_all()  # Elimina todas las tablas existentes
    db.create_all()  # Crea todas las tablas desde cero

    # Comprobar si las tablas se han creado
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"✅ Tablas creadas: {tables}")

    # Imprimir estructura de cada tabla
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n📌 Estructura de la tabla '{table}':")
        for column in columns:
            print(f" - {column['name']} ({column['type']})")

    print("\n🎉 Base de datos creada correctamente.")
