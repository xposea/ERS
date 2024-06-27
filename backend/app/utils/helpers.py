from fastapi import WebSocket
from typing import List, Dict
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, lobby_id: str):
        if lobby_id not in self.active_connections:
            self.active_connections[lobby_id] = []
        self.active_connections[lobby_id].append(websocket)
        logger.info(f"Added connection to lobby {lobby_id}. Total connections: {len(self.active_connections[lobby_id])}")

    async def disconnect(self, websocket: WebSocket, lobby_id: str):
        if lobby_id in self.active_connections:
            self.active_connections[lobby_id].remove(websocket)
            logger.info(f"Removed connection from lobby {lobby_id}. Remaining connections: {len(self.active_connections[lobby_id])}")
            if not self.active_connections[lobby_id]:
                del self.active_connections[lobby_id]
                logger.info(f"Lobby {lobby_id} is now empty and has been removed")

    async def broadcast_to_lobby(self, lobby_id: str, message: str, exclude: WebSocket = None):
        if lobby_id in self.active_connections:
            for connection in self.active_connections[lobby_id]:
                if connection != exclude:
                    try:
                        await connection.send_text(message)
                    except Exception as e:
                        logger.error(f"Failed to send message to a connection in lobby {lobby_id}: {str(e)}")