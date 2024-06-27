import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from starlette.websockets import WebSocketState
# from .routers import auth, user, game, ranking
from .utils.helpers import ConnectionManager
from .services.game_service import GameService
import json
# import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Include routers
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(user.router, prefix="/users", tags=["users"])
# app.include_router(game.router, prefix="/games", tags=["games"])
# app.include_router(ranking.router, prefix="/rankings", tags=["rankings"])

manager = ConnectionManager()
game_service = GameService()


async def send_error(websocket: WebSocket, message: str):
    if websocket.client_state == WebSocketState.CONNECTED:
        await websocket.send_json({"type": "error", "message": message})


@app.websocket("/ws/{lobby_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str, player_name: str):
    await manager.connect(websocket, lobby_id, player_name)
    try:
        while True:
            data = await websocket.receive_text()
            action = json.loads(data)

            if action['type'] == 'join_lobby':
                player_count = game_service.join_lobby(lobby_id, player_name)
                await manager.broadcast_to_lobby(json.dumps({
                    "type": "player_joined",
                    "player": player_name,
                    "player_count": player_count
                }), lobby_id)

            elif action['type'] == 'start_game':
                game, error = game_service.start_game(lobby_id)
                if game:
                    await manager.broadcast_to_lobby(json.dumps({
                        "type": "game_started",
                        "players": [player.name for player in game.players]
                    }), lobby_id)
                else:
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": f"Cannot start game: {error}"
                    }), lobby_id, player_name)

            elif action['type'] == 'play':
                success, result, data = game_service.play_turn(lobby_id, player_name)
                if success:
                    if result == "game_over":
                        await manager.broadcast_to_lobby(json.dumps({
                            "type": "game_over",
                            "winner": data
                        }), lobby_id)
                    else:
                        await manager.broadcast_to_lobby(json.dumps({
                            "type": "card_played",
                            "player": player_name
                        }), lobby_id)
                        if game_service.can_slap(lobby_id):
                            await manager.broadcast_to_lobby(json.dumps({
                                "type": "slap_opportunity"
                            }), lobby_id)
                else:
                    await manager.send_personal_message(json.dumps({
                        "type": "error",
                        "message": data
                    }), lobby_id, player_name)

            elif action['type'] == 'slap':
                success, slap_time = game_service.attempt_slap(lobby_id, player_name)
                await manager.broadcast_to_lobby(json.dumps({
                    "type": "slap",
                    "player": player_name,
                    "success": success,
                    "time": slap_time if success else None
                }), lobby_id)

            # Send updated game state after each action
            game_state = game_service.get_state(lobby_id)
            if game_state:
                await manager.broadcast_to_lobby(json.dumps({
                    "type": "game_state",
                    "state": game_state
                }), lobby_id)

    except WebSocketDisconnect:
        await manager.disconnect(lobby_id, player_name)
        await manager.broadcast_to_lobby(json.dumps({
            "type": "player_left",
            "player": player_name
        }), lobby_id)


@app.get("/")
async def root():
    return {"message": "ERS Game Server"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"detail": exc.detail}, exc.status_code


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
