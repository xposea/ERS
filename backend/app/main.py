import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from .routers import auth, user, game, ranking
from .utils.helpers import ConnectionManager
from .services.game_service import GameService
import json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(game.router, prefix="/games", tags=["games"])
app.include_router(ranking.router, prefix="/rankings", tags=["rankings"])

manager = ConnectionManager()
game_service = GameService()


@app.websocket("/ws/{lobby_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str, player_name: str):
    await manager.connect(websocket)
    try:
        logger.info(f"Player {player_name} connected to lobby {lobby_id}")
        game_service.create_lobby(lobby_id)
        game_service.join_lobby(lobby_id, player_name)
        await manager.broadcast_to_lobby(lobby_id, json.dumps({
            "type": "player_joined",
            "player": player_name
        }))

        while True:
            data = await websocket.receive_text()
            action = json.loads(data)
            logger.debug(f"Received action: {action}")

            if action['type'] == 'start_game':
                game, error = game_service.start_game(lobby_id)
                if game:
                    logger.info(f"Game started in lobby {lobby_id}")
                    await manager.broadcast_to_lobby(lobby_id, json.dumps({
                        "type": "game_started",
                        "players": [player.name for player in game.players]
                    }))
                else:
                    logger.warning(f"Failed to start game in lobby {lobby_id}: {error}")
                    await websocket.send_json({"type": "error", "message": f"Cannot start game: {error}"})
            elif action['type'] == 'play':
                if game_service.play_turn(lobby_id, player_name):
                    if game_service.can_slap(lobby_id):
                        await manager.broadcast_to_lobby(lobby_id, json.dumps({"type": "slap_opportunity"}))
                else:
                    await websocket.send_json({"type": "error", "message": "Not your turn or invalid play"})
            elif action['type'] == 'slap':
                if game_service.attempt_slap(lobby_id, player_name):
                    await manager.broadcast_to_lobby(lobby_id, json.dumps(
                        {"type": "slap", "player": player_name, "success": True}))
                else:
                    await manager.broadcast_to_lobby(lobby_id, json.dumps(
                        {"type": "slap", "player": player_name, "success": False}))

            # Broadcast updated game state
            await manager.broadcast_to_lobby(lobby_id, json.dumps(game_service.get_state(lobby_id)))
    except WebSocketDisconnect:
        logger.info(f"Player {player_name} disconnected from lobby {lobby_id}")
        manager.disconnect(websocket)
        game_service.remove_player(lobby_id, player_name)
        await manager.broadcast_to_lobby(lobby_id, json.dumps({
            "type": "player_left",
            "player": player_name
        }))
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        await websocket.close(code=1011)  # Internal error


@app.get("/")
async def root():
    return {"message": "ERS Game Server"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"detail": exc.detail}, exc.status_code


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
