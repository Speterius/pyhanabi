import socketserver
import common.packets as data_packets
from .tcp_server import TCPServer
from typing import Tuple
import game.game_settings as game_settings
import time


class RequestHandler(socketserver.StreamRequestHandler):
    """ Handle the data flow with the connected clients. """

    def __init__(self, request, client_address: Tuple[str, int], server: TCPServer):
        super().__init__(request, client_address, server)

    def setup(self):
        print(f'Connecting networking with address: {self.client_address}.')
        self.server.add_client(self)

    def send_game_state(self, data):
        self.request.send(data)

    def handle(self):

        """ Continuosly wait for a data packet and handle two scenarios:
        1) connection attempts until max players is reached
        2) player events -> which will update the server game state. """

        while True:
            # Receive a data packet:
            try:
                data = self.request.recv(self.server.BUFFERSIZE)
            except ConnectionResetError as ex:
                print('Client disconnected.', ex)
                return
            if not data:
                continue

            # Decode the data packet and convert it back to a DataPacket object
            data = data_packets.load(data)

            # If the networking is trying to establish connection handshake:
            if type(data) is data_packets.ConnectionAttempt:

                # Accept players until we reach MAX count:
                if self.server.player_count < game_settings.MAX_PLAYERS:

                    # Store player data in server's dictionary:
                    player_id = self.server.player_count
                    self.server.players[player_id] = data.user_name

                    # Confirm connection handshake and player id sync:
                    response = data_packets.ConnectionConfirmed(True, data.user_name, player_id)
                    self.request.send(response.to_bytes())

                    # Increase player count, if we reached max_player: start the game:
                    self.server.player_count += 1
                    if self.server.player_count == game_settings.MAX_PLAYERS:
                        self.server.start_game()

                    # Wait a bit for the networking to start its threads and send the initial game state update:
                    time.sleep(0.2)
                    self.server.broadcast_game_state_update()

                    continue

                else:

                    # Deny connection when above MAX player count is reached and disconnect the networking:
                    response = data_packets.ConnectionConfirmed(False, data.user_name, 999)
                    self.request.send(response.to_bytes())

                    return

            elif type(data) in data_packets.get_events():
                print('Updating Game State (...) \n pass')

                self.server.update_game_state(event=data)
                self.server.broadcast_game_state_update()

    def finish(self):
        print(f'Disconnecting networking with address: {self.client_address}!')
        self.server.remove_client(self)
        try:
            super().finish()
        except AttributeError as ex:
            print('RequestHandler finish() dropped exception:', ex)
