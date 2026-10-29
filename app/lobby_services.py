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

def get_connection():
    """Helper to get a database connection."""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def init_db():
    """Creates the tables if they do not exist."""
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
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(lobby_id, nickname)
            );
        """)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def create_lobby(room_name: str, host_nickname: str) -> dict:
    init_db()  # Ensures tables exist
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

        # Add the host to the lobby players
        cursor.execute(
            "INSERT INTO lobby_players (lobby_id, nickname) VALUES (%s, %s);",
            (lobby_id, host_nickname)
        )
        
        conn.commit()
        return {
            "success": True,
            "lobby_id": lobby_id,
            "room_name": lobby["name"],
            "status": lobby["status"],
            "host": host_nickname
        }
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


def join_lobby(room_name: str, nickname: str) -> dict:
    """
    Adds a user to a lobby by room name if it exists and is waiting.
    Fails if the nickname is already taken in that lobby.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if lobby exists by room name and is accepting players
        cursor.execute("SELECT id, status FROM lobbies WHERE name = %s;", (room_name,))
        lobby = cursor.fetchone()
        
        if not lobby:
            return {"success": False, "error": "Lobby not found."}
        if lobby["status"] != "waiting":
            return {"success": False, "error": "Game has already started or finished."}

        # Attempt to insert player using the found lobby id
        cursor.execute(
            "INSERT INTO lobby_players (lobby_id, nickname) VALUES (%s, %s);",
            (lobby["id"], nickname)
        )
        conn.commit()
        return {"success": True, "message": f"Successfully joined lobby '{room_name}' as {nickname}."}
        
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"success": False, "error": "This nickname is already taken in this lobby."}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()

def get_lobby_players(room_name: str) -> dict:
    """
    Returns lobby details and a list of all players using the room name.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Find the lobby by its name
        cursor.execute("SELECT id, name, status FROM lobbies WHERE name = %s;", (room_name,))
        lobby = cursor.fetchone()
        
        if not lobby:
            return {"success": False, "error": "Lobby not found."}

        # 2. Get all players in this lobby
        cursor.execute(
            "SELECT nickname, joined_at FROM lobby_players WHERE lobby_id = %s ORDER BY joined_at ASC;",
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