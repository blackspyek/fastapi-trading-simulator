from typing import List, Dict, Any
from fastapi import WebSocket

class ConnectionManager:
    """
    Class managing active WebSocket connections.
    Stores a list of clients and enables broadcasting messages to them.
    """

    def __init__(self) -> None:
        """
        Initializes an empty list of active connections.
        """
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accepts an incoming WebSocket connection and adds it to the list.

        Args:
            websocket (WebSocket): Client connection instance.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Removes a connection from the list of active clients.
        Synchronous method since it only operates on the in-memory list.

        Args:
            websocket (WebSocket): Connection to remove.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Sends a JSON message to all connected clients.
        In case of a sending error (e.g., client disconnected), removes the client from the list.

        Args:
            message (Dict[str, Any]): Dictionary of data to send as JSON.
        """
        # Iterating over a copy of the list [:] to safely modify the original list if needed
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager: ConnectionManager = ConnectionManager()