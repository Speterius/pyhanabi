import socketserver
from game.game_logic import GameState
import game.game_settings as settings
from .request_handler import RequestHandler
from typing import Tuple


class TCPServer(socketserver.ThreadingTCPServer):

    """ Handle TCP connections and all Player Events to update and broadcast the Game state """

    def __init__(self, server_address: Tuple[str, int] = ('localhost', 10000), request_handler_class: type = RequestHandler):
        self.address = server_address
        self.IP: str = server_address[0]
        self.PORT: int = server_address[1]
        self.BUFFERSIZE: int = 4096
        self.clients: set = set()
        super().__init__(server_address, request_handler_class)

        # Player connections:
        self.player_count: int = 0
        self.players: dict = {}

        # Game State:
        self.GS: GameState = GameState(settings.MAX_PLAYERS)

    def add_client(self, client):
        self.clients.add(client)

    def broadcast_game_state_update(self):
        """ Send the GS game state to all the connected clients."""

        for client in tuple(self.clients):
            client.send_game_state(self.GS.to_bytes(self.players))

    def remove_client(self, client):
        self.clients.remove(client)

    def start_game(self):
        print('Starting game...')
        self.GS.started = True
        self.broadcast_game_state_update()

    def update_game_state(self, event):
        self.GS.update(event=event)
