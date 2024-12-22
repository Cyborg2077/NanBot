import asyncio

from starlette.websockets import WebSocket


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections = {}

    def add_connection(self, client_id: str, websocket: WebSocket):
        self.active_connections[client_id] = websocket

    def remove_connection(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    def get_connection(self, client_id: str) -> WebSocket:
        return self.active_connections.get(client_id)

    def send_message(self, client_id: str, message: str):
        websocket = self.get_connection(client_id)
        if websocket:
            asyncio.create_task(websocket.send_text(message))

    def get_active_connections(self):
        return list(self.active_connections.values())


def get_connection_manager() -> WebSocketConnectionManager:
    if not hasattr(get_connection_manager, 'instance'):
        get_connection_manager.instance = WebSocketConnectionManager()
    return get_connection_manager()
