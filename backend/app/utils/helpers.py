from fastapi import WebSocket
from typing import List, Dict
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  # Dictionary of dictionaries, keyed by lobby_id then player_name

    async def connect(self, websocket: WebSocket, lobby_id: str, player_name: str):
        await websocket.accept()
        if lobby_id not in self.active_connections:
            self.active_connections[lobby_id] = {}
        self.active_connections[lobby_id][player_name] = websocket

    async def disconnect(self, lobby_id: str, player_name: str):
        if lobby_id in self.active_connections and player_name in self.active_connections[lobby_id]:
            del self.active_connections[lobby_id][player_name]
            if not self.active_connections[lobby_id]:
                del self.active_connections[lobby_id]

    async def send_personal_message(self, message: str, lobby_id: str, player_name: str):
        if lobby_id in self.active_connections and player_name in self.active_connections[lobby_id]:
            await self.active_connections[lobby_id][player_name].send_text(message)

    async def broadcast_to_lobby(self, message: str, lobby_id: str, exclude: str = None):
        if lobby_id in self.active_connections:
            for player_name, connection in self.active_connections[lobby_id].items():
                if player_name != exclude:
                    await connection.send_text(message)

    def get_lobby_player_count(self, lobby_id: str):
        return len(self.active_connections.get(lobby_id, {}))
