import sqlite3

def view_database(db_path="instance/games.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📂 Contenido de la base de datos \"games.db\":")
        
        # Mostrar juegos
        print("\n🎮 Tabla: games")
        cursor.execute("SELECT * FROM game")
        games = cursor.fetchall()
        for game in games:
            print(game)
        
        # Mostrar logros
        print("\n🏆 Tabla: achievements")
        cursor.execute("SELECT * FROM achievement")
        achievements = cursor.fetchall()
        for achievement in achievements:
            print(achievement)
        
        # Mostrar usuarios
        print("\n👤 Tabla: users")
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()
        for user in users:
            print(user)
        
        conn.close()
    except Exception as e:
        print(f"❌ Error al leer la base de datos: {e}")

if __name__ == "__main__":
    view_database()