import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection details for Docker environment
DB_CONFIG = {
    "dbname": "bunker_db",
    "user": "root",
    "password": "root",
    "host": "postgres_db",
    "port": 5432
}

VALID_ROLES = {"SPECTATOR", "GAME_MASTER", "PLAYER"}

def get_connection():
    """Helper to get a database connection."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def init_db():
    """Creates the tables if they do not exist and updates schema if needed."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lobbies (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS lobby_players (
                id SERIAL PRIMARY KEY,
                lobby_id INT REFERENCES lobbies(id) ON DELETE CASCADE,
                nickname VARCHAR(50) NOT NULL,
                role VARCHAR(20) DEFAULT 'PLAYER',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(lobby_id, nickname)
            );
        """)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def create_lobby(room_name: str, host_nickname: str) -> dict:
    """Creates a lobby and assigns the host as the GAME_MASTER."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Insert the new lobby
        cursor.execute(
            "INSERT INTO lobbies (name, status) VALUES (%s, 'waiting') RETURNING id, name, status;",
            (room_name,)
        )
        lobby = cursor.fetchone()
        lobby_id = lobby["id"]

        # Add the host as GAME_MASTER
        cursor.execute(
            "INSERT INTO lobby_players (lobby_id, nickname, role) VALUES (%s, %s, 'GAME_MASTER');",
            (lobby_id, host_nickname)
        )
        
        conn.commit()
        return {
            "success": True,
            "lobby_id": lobby_id,
            "room_name": lobby["name"],
            "status": lobby["status"],
            "host": host_nickname,
            "role": "GAME_MASTER"
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def join_lobby(room_name: str, nickname: str, requested_role: str = "PLAYER") -> dict:
    """
    Adds a user to a lobby. Enforces max 12 PLAYERS and max 1 GAME_MASTER.
    """
    init_db()
    
    if requested_role not in VALID_ROLES:
        return {"success": False, "error": f"Invalid role. Choose from {list(VALID_ROLES)}."}

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if lobby exists and is accepting players
        cursor.execute("SELECT id, status FROM lobbies WHERE name = %s;", (room_name,))
        lobby = cursor.fetchone()
        
        if not lobby:
            return {"success": False, "error": "Lobby not found."}
        if lobby["status"] != "waiting":
            return {"success": False, "error": "Game has already started or finished."}

        lobby_id = lobby["id"]

        # Only 1 Game Master per lobby
        if requested_role == "GAME_MASTER":
            cursor.execute("SELECT COUNT(*) AS count FROM lobby_players WHERE lobby_id = %s AND role = 'GAME_MASTER';", (lobby_id,))
            if cursor.fetchone()["count"] > 0:
                return {"success": False, "error": "This lobby already has a Game Master."}

        # No more than 12 Players
        if requested_role == "PLAYER":
            cursor.execute("SELECT COUNT(*) AS count FROM lobby_players WHERE lobby_id = %s AND role = 'PLAYER';", (lobby_id,))
            if cursor.fetchone()["count"] >= 12:
                return {"success": False, "error": "Lobby has reached the maximum limit of 12 players."}

        # Attempt to insert player with role
        cursor.execute(
            "INSERT INTO lobby_players (lobby_id, nickname, role) VALUES (%s, %s, %s);",
            (lobby_id, nickname, requested_role)
        )
        conn.commit()
        return {"success": True, "message": f"Successfully joined lobby '{room_name}' as {nickname} ({requested_role})."}
        
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"success": False, "error": "This nickname is already taken in this lobby."}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def update_player_role(room_name: str, nickname: str, new_role: str) -> dict:
    """
    Changes an existing player's role while respecting lobby limits 
    (Max 1 GAME_MASTER, Max 12 PLAYERS).
    """
    init_db()
    
    if new_role not in VALID_ROLES:
        return {"success": False, "error": f"Invalid role. Choose from {list(VALID_ROLES)}."}

    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get lobby ID
        cursor.execute("SELECT id FROM lobbies WHERE name = %s;", (room_name,))
        lobby = cursor.fetchone()
        if not lobby:
            return {"success": False, "error": "Lobby not found."}
        
        lobby_id = lobby["id"]

        # Verify player exists in this lobby
        cursor.execute("SELECT id, role FROM lobby_players WHERE lobby_id = %s AND nickname = %s;", (lobby_id, nickname))
        player = cursor.fetchone()
        if not player:
            return {"success": False, "error": "Player not found in this lobby."}

        # If changing to GAME_MASTER, check if one already exists
        if new_role == "GAME_MASTER" and player["role"] != "GAME_MASTER":
            cursor.execute("SELECT COUNT(*) AS count FROM lobby_players WHERE lobby_id = %s AND role = 'GAME_MASTER';", (lobby_id,))
            if cursor.fetchone()["count"] > 0:
                return {"success": False, "error": "A Game Master already exists in this lobby."}

        # If changing to PLAYER, check if player count is under 12
        if new_role == "PLAYER" and player["role"] != "PLAYER":
            cursor.execute("SELECT COUNT(*) AS count FROM lobby_players WHERE lobby_id = %s AND role = 'PLAYER';", (lobby_id,))
            if cursor.fetchone()["count"] >= 12:
                return {"success": False, "error": "Lobby has reached the maximum limit of 12 players."}

        # Update the role
        cursor.execute(
            "UPDATE lobby_players SET role = %s WHERE lobby_id = %s AND nickname = %s;",
            (new_role, lobby_id, nickname)
        )
        conn.commit()
        return {"success": True, "message": f"Successfully updated {nickname}'s role to {new_role}."}

    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def get_lobby_players(room_name: str) -> dict:
    """
    Returns lobby details and a list of all players with their roles.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, name, status FROM lobbies WHERE name = %s;", (room_name,))
        lobby = cursor.fetchone()
        
        if not lobby:
            return {"success": False, "error": "Lobby not found."}

        cursor.execute(
            "SELECT nickname, role, joined_at FROM lobby_players WHERE lobby_id = %s ORDER BY joined_at ASC;",
            (lobby["id"],)
        )
        players = cursor.fetchall()

        return {
            "success": True,
            "room_name": lobby["name"],
            "status": lobby["status"],
            "players": [dict(p) for p in players]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()