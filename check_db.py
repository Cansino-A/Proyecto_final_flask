import requests

# 🔹 Configurar la API Key
RIOT_API_KEY = "RGAPI-1159207e-648b-4eaf-8846-ff3feaa49772"  # Reemplázala con tu API Key válida
BASE_ACCOUNT_URL = "https://europe.api.riotgames.com"
BASE_MATCH_URL = "https://europe.api.riotgames.com"

# 🔹 Datos del jugador a buscar
game_name = "Un tio bueno"  # Nombre del invocador
tag_line = "EUW"  # Región del Riot ID (ej: EUW, NA, BR)

def get_puuid(game_name, tag_line):
    """ Obtiene el PUUID del jugador a partir de su Riot ID """
    url = f"{BASE_ACCOUNT_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        puuid = response.json().get("puuid", "")
        print(f"\n✅ PUUID del jugador: {puuid}")
        return puuid
    else:
        print(f"\n❌ Error {response.status_code}: {response.json()}")
        return None

def get_match_history(puuid):
    """ Obtiene el historial de partidas del jugador (últimas 5 partidas) """
    url = f"{BASE_MATCH_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_ids = response.json()
        print("\n✅ Últimas 5 partidas:")
        for match_id in match_ids:
            print(f"🔹 {match_id}")
        return match_ids
    else:
        print(f"\n❌ Error {response.status_code}: {response.json()}")
        return None

def get_match_details(match_id):
    """ Obtiene detalles de una partida específica """
    url = f"{BASE_MATCH_URL}/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        match_data = response.json()
        print("\n✅ Detalles de la partida:")
        
        # Extraer información relevante
        game_mode = match_data["info"]["gameMode"]
        duration = match_data["info"]["gameDuration"] // 60  # Convertir a minutos
        
        print(f"🔹 Modo de juego: {game_mode}")
        print(f"🔹 Duración: {duration} minutos")

        # Buscar el jugador en la partida
        for participant in match_data["info"]["participants"]:
            if participant["puuid"] == puuid:
                print(f"\n🎮 Jugador: {participant['summonerName']}")
                print(f"🔹 Campeón: {participant['championName']}")
                print(f"🔹 KDA: {participant['kills']}/{participant['deaths']}/{participant['assists']}")
                print(f"🔹 Ganó la partida: {'Sí' if participant['win'] else 'No'}")
                break
    else:
        print(f"\n❌ Error {response.status_code}: {response.json()}")

# 🔹 EJECUTAR TODO EL PROCESO
puuid = get_puuid(game_name, tag_line)

if puuid:
    match_ids = get_match_history(puuid)

    if match_ids:
        # Obtener detalles de la primera partida en el historial
        get_match_details(match_ids[0])
