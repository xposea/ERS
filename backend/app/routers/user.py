from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()


class User(BaseModel):
    username: str
    email: str


@router.post("/users/", response_model=User)
async def create_user(user: User):
    # Implement user creation logic here
    return user


@router.get("/users/{username}", response_model=User)
async def read_user(username: str):
    # Implement user retrieval logic here
    return {"username": username, "email": f"{username}@example.com"}
