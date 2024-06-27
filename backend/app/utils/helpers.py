from fastapi import WebSocket
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        lobby_id = websocket.path_params['lobby_id']
        if lobby_id not in self.active_connections:
            self.active_connections[lobby_id] = []
        self.active_connections[lobby_id].append(websocket)

    def disconnect(self, websocket: WebSocket):
        lobby_id = websocket.path_params['lobby_id']
        self.active_connections[lobby_id].remove(websocket)

    async def broadcast_to_lobby(self, lobby_id: str, message: str):
        if lobby_id in self.active_connections:
            for connection in self.active_connections[lobby_id]:
                await connection.send_text(message)
