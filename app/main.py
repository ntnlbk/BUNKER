from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.websocket_manager import manager

import app.lobby_services as lobby_services

app = FastAPI(title="Bunker Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateLobbyRequest(BaseModel):
    host_name: str
    room_code: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("app/UI/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/lobbies/create")
def create_lobby(payload: CreateLobbyRequest):
    print("Received request to create lobby:", payload.host_name, payload.room_code)
    result = lobby_services.create_lobby(payload.room_code, payload.host_name)
    print("Lobby creation result:", result)
    if(not result["success"]):
        return {"status": "error", "message": result["error"]}
    return {
        "status": "success",
        "room_code": result["room_name"],
        "host_name": payload.host_name,
    }

@app.get("/api/lobbies/{room_name}/players")
def get_lobby_players_endpoint(room_name: str):
    result = lobby_services.get_lobby_players(room_name)
    if not result["success"]:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": result["error"]}
        )
    return result

@app.get("/lobby",  response_class=HTMLResponse)
def serve_lobby():
    with open("app/UI/lobby.html", "r", encoding="utf-8") as f:
        return f.read()

class JoinLobbyRequest(BaseModel):
    room_name: str
    nickname: str
    role: str

@app.post("/api/lobbies/join")
def join_lobby_endpoint(payload: JoinLobbyRequest):
    print(f"Received request to join lobby '{payload.room_name}' as {payload.nickname}")
    
    # Call your corrected backend service function
    result = lobby_services.join_lobby(payload.room_name, payload.nickname, payload.role)
    
    if not result["success"]:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "message": result["error"]}
        )
        
    return {
        "status": "success",
        "room_name": payload.room_name,
        "nickname": payload.nickname,
        "message": result["message"]
    }

@app.get("/game/gm", response_class=HTMLResponse)
def serve_gm_game():
    with open("app/UI/gm.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/game/player", response_class=HTMLResponse)
def serve_player_game():
    with open("app/UI/player.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/game/spectator", response_class=HTMLResponse)
def serve_spectator_game():
    with open("app/UI/spectator.html", "r", encoding="utf-8") as f:
        return f.read()

@app.websocket("/ws/{room_code}/{nickname}")
async def websocket_endpoint(websocket: WebSocket, room_code: str, nickname: str):
    await manager.connect(room_code, websocket)
    await manager.broadcast(room_code, {
        "type": "CHAT",
        "sender": "SYSTEM",
        "message": f"{nickname} connected to the frequency."
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "START_GAME":
                # Broadcast game start event along with target route or role info
                await manager.broadcast(room_code, {
                    "type": "GAME_STARTED"
                })
            elif event_type == "CHAT":
                await manager.broadcast(room_code, {
                    "type": "CHAT",
                    "sender": nickname,
                    "message": data.get("message", "")
                })
    except WebSocketDisconnect:
        manager.disconnect(room_code, websocket)
        await manager.broadcast(room_code, {
            "type": "CHAT",
            "sender": "SYSTEM",
            "message": f"{nickname} disconnected."
        })