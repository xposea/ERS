# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from typing import List
#
# router = APIRouter()
#
#
# class GameState(BaseModel):
#     id: str
#     players: List[str]
#     current_player: str
#     pile_count: int
#
#
# @router.post("/games/", response_model=GameState)
# async def create_game():
#     # Implement game creation logic here
#     return {"id": "game123", "players": [], "current_player": "", "pile_count": 0}
#
#
# @router.get("/games/{game_id}", response_model=GameState)
# async def get_game_state(game_id: str):
#     # Implement game state retrieval logic here
#     return {"id": game_id, "players": ["player1", "player2"], "current_player": "player1", "pile_count": 10}
#
#
# @router.post("/games/{game_id}/join")
# async def join_game(game_id: str, player_name: str):
#     # Implement game joining logic here
#     return {"message": f"{player_name} joined game {game_id}"}
