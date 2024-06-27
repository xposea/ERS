import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from starlette.websockets import WebSocketState
from .routers import auth, user, game, ranking
from .utils.helpers import ConnectionManager
from .services.game_service import GameService
import json
import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(game.router, prefix="/games", tags=["games"])
app.include_router(ranking.router, prefix="/rankings", tags=["rankings"])

manager = ConnectionManager()
game_service = GameService()


async def send_error(websocket: WebSocket, message: str):
    if websocket.client_state == WebSocketState.CONNECTED:
        await websocket.send_json({"type": "error", "message": message})


@app.websocket("/ws/{lobby_id}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str, player_name: str):
    logger.info(f"Attempting to connect player {player_name} to lobby {lobby_id}")
    try:
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for player {player_name} in lobby {lobby_id}")
        await manager.connect(websocket, lobby_id)
        logger.info(f"Player {player_name} connected to lobby {lobby_id}")

        try:
            while True:
                if websocket.client_state == WebSocketState.DISCONNECTED:
                    logger.warning(f"WebSocket for {player_name} in lobby {lobby_id} is in DISCONNECTED state")
                    break

                data = await websocket.receive_text()
                logger.debug(f"Received data from {player_name}: {data}")

                try:
                    action = json.loads(data)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received from {player_name}: {data}")
                    await send_error(websocket, "Invalid JSON received")
                    continue

                logger.info(f"Received action from {player_name}: {action}")

                if action['type'] == 'join_lobby':
                    player_count = game_service.join_lobby(lobby_id, player_name)
                    logger.info(f"Player {player_name} joined lobby {lobby_id}. Total players: {player_count}")
                    await manager.broadcast_to_lobby(lobby_id, json.dumps({
                        "type": "player_joined",
                        "player": player_name,
                        "player_count": player_count
                    }), exclude=websocket)

                elif action['type'] == 'start_game':
                    logger.info(f"Attempting to start game in lobby {lobby_id}")
                    game, error = game_service.start_game(lobby_id)
                    if game:
                        logger.info(f"Game started in lobby {lobby_id}")
                        start_message = json.dumps({
                            "type": "game_started",
                            "players": [player.name for player in game.players]
                        })
                        await manager.broadcast_to_lobby(lobby_id, start_message)
                    else:
                        logger.warning(f"Failed to start game in lobby {lobby_id}: {error}")
                        await send_error(websocket, f"Cannot start game: {error}")

                elif action['type'] == 'play':
                    logger.info(f"Player {player_name} attempting to play a card")
                    success, result, data = game_service.play_turn(lobby_id, player_name)
                    if success:
                        if result == "game_over":
                            # Send final game state before game_over message
                            final_game_state = game_service.get_state(lobby_id)
                            await manager.broadcast_to_lobby(lobby_id, json.dumps({
                                "type": "game_state",
                                "state": final_game_state
                            }))
                            # Then send game_over message
                            await manager.broadcast_to_lobby(lobby_id, json.dumps({
                                "type": "game_over",
                                "winner": data
                            }))
                            # Clean up the game
                            del game_service.games[lobby_id]
                        else:
                            await manager.broadcast_to_lobby(lobby_id, json.dumps({
                                "type": "card_played",
                                "player": player_name
                            }))
                            if game_service.can_slap(lobby_id):
                                await manager.broadcast_to_lobby(lobby_id, json.dumps({
                                    "type": "slap_opportunity"
                                }))
                    else:
                        await send_error(websocket, data)

                elif action['type'] == 'slap':
                    logger.info(f"Player {player_name} attempting to slap")
                    success, slap_time = game_service.attempt_slap(lobby_id, player_name)
                    await manager.broadcast_to_lobby(lobby_id, json.dumps({
                        "type": "slap",
                        "player": player_name,
                        "success": success,
                        "time": slap_time if success else None
                    }))

                else:
                    logger.warning(f"Unknown action type received from {player_name}: {action['type']}")
                    await send_error(websocket, f"Unknown action type: {action['type']}")

                # Send updated game state after each action
                game_state = game_service.get_state(lobby_id)
                if game_state:
                    await manager.broadcast_to_lobby(lobby_id, json.dumps({
                        "type": "game_state",
                        "state": game_state
                    }))

                    if game_state.get("is_game_over", False):
                        logger.info(f"Game over in lobby {lobby_id}. Winner: {game_state.get('winner')}")
                        await manager.broadcast_to_lobby(lobby_id, json.dumps({
                            "type": "game_over",
                            "winner": game_state.get("winner")
                        }))
                        break
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for {player_name} in lobby {lobby_id}")
        except Exception as e:
            logger.error(f"An error occurred for {player_name} in lobby {lobby_id}: {str(e)}")
            logger.error(traceback.format_exc())
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection for {player_name} in lobby {lobby_id}: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        logger.info(f"Cleaning up connection for {player_name} in lobby {lobby_id}")
        await manager.disconnect(websocket, lobby_id)
        # game_service.remove_player(lobby_id, player_name)
        await manager.broadcast_to_lobby(lobby_id, json.dumps({
            "type": "player_left",
            "player": player_name
        }))


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