from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class PlayerRank(BaseModel):
    username: str
    rank: int
    wins: int


@router.get("/rankings", response_model=List[PlayerRank])
async def get_rankings():
    # Implement rankings retrieval logic here
    return [
        {"username": "player1", "rank": 1, "wins": 10},
        {"username": "player2", "rank": 2, "wins": 8},
    ]
