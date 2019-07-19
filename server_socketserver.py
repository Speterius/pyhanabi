import socketserver
import packets
import time
from settings import *
from game_logic import GameState


class RequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        print(f'Connecting client with address: {self.client_address}.')

    def handle(self):
        while True:
            # Receive a data packet and decode it:
            data = self.request.recv(self.server.BUFFERSIZE)

            if not data:
                continue

            # Decode the data packet and convert back to a DataPacket class
            data = packets.load(data)

            # If the data packet is a packets.ConnectionAttempt:
            if type(data) is packets.ConnectionAttempt:

                    if self.server.player_count < MAX_PLAYERS:

                        # Store player in server's dictionary:
                        player_id = self.server.player_count
                        self.server.players[player_id] = data.user_name

                        # Confirm:
                        response = packets.ConnectionConfirmed(True, data.user_name, player_id)
                        self.request.send(response.to_bytes())

                        # Increase player count:
                        self.server.player_count += 1

                        # Wait a bit for the client to start threads and send the initial game state update:
                        game_state_update = self.server.GS.to_bytes(self.server.players)
                        time.sleep(0.2)
                        self.request.send(game_state_update)

                        continue

                    else:

                        # Deny connection:
                        response = packets.ConnectionConfirmed(False, data.user_name, 999)
                        self.request.send(response.to_bytes())

                        return

            elif type(data) in packets.get_events():
                print('Updating Game State (...) \n pass')

    def finish(self):
        print(f'Disconnecting client with address: {self.client_address}!')


class Server(socketserver.ThreadingTCPServer):
    def __init__(self, request_handler):
        self.PORT = 10000
        self.BUFFERSIZE = 4096
        super().__init__(('localhost', self.PORT), request_handler)

        # Player connections:
        self.player_count = 0
        self.players = {}

        # Game State:
        self.GS = GameState(MAX_PLAYERS)


def main():
    server = Server(RequestHandler)
    server.serve_forever()
    return 0


if __name__ == '__main__':
    main()
