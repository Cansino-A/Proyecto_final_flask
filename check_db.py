import sqlite3

def view_games_with_achievements(db_path="instance/games.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📂 Contenido de la base de datos \"games.db\":")
        
        # Consulta para obtener los juegos con sus logros
        query = """
        SELECT 
            g.id AS game_id,
            g.appid,
            g.name AS game_name,
            g.playtime,
            g.image,
            a.id AS achievement_id,
            a.name AS achievement_name,
            a.description,
            a.achieved,
            a.unlock_time
        FROM 
            game g
        LEFT JOIN 
            achievement a ON g.id = a.game_id
        ORDER BY 
            g.id, a.id;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Mostrar los resultados
        current_game_id = None
        for row in results:
            game_id, appid, game_name, playtime, image, achievement_id, achievement_name, description, achieved, unlock_time = row
            
            # Mostrar el juego solo si es diferente al anterior
            if game_id != current_game_id:
                print(f"\n🎮 Juego: {game_name} (ID: {game_id}, AppID: {appid})")
                print(f"   - Playtime: {playtime} horas")
                print(f"   - Imagen: {image}")
                current_game_id = game_id
            
            # Mostrar los logros del juego
            if achievement_id is not None:
                print(f"   🏆 Logro: {achievement_name}")
                print(f"      - Descripción: {description}")
                print(f"      - Desbloqueado: {'Sí' if achieved else 'No'}")
                print(f"      - Fecha de desbloqueo: {unlock_time}")
            else:
                print("   🏆 No se han desbloqueado logros para este juego.")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error al leer la base de datos: {e}")

if __name__ == "__main__":
    view_games_with_achievements()