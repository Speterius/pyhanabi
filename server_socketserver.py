import queue
import socketserver
import packets
import time
from settings import *
from game_logic import GameState


class RequestHandler(socketserver.StreamRequestHandler):

    """ Handle all data flow with the connected clients. """

    def __init__(self, request, client_address, server):
        self.buffer = queue.Queue()
        super().__init__(request, client_address, server)

    def setup(self):
        print(f'Connecting client with address: {self.client_address}.')
        self.server.add_client(self)

    def send_game_state(self, data):
        self.request.send(data)

    def handle(self):
        while True:
            # Receive a data packet and decode it:
            try:
                data = self.request.recv(self.server.BUFFERSIZE)
            except ConnectionResetError as ex:
                print('Client disconnected.', ex)
                return

            if not data:
                continue

            # Decode the data packet and convert back to a DataPacket object
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
                        if self.server.player_count == MAX_PLAYERS:
                            self.server.start_game()

                        # Wait a bit for the client to start threads and send the initial game state update:
                        time.sleep(0.2)
                        self.server.broadcast_game_state_update()

                        continue

                    else:

                        # Deny connection:
                        response = packets.ConnectionConfirmed(False, data.user_name, 999)
                        self.request.send(response.to_bytes())

                        return

            elif type(data) in packets.get_events():
                print('Updating Game State (...) \n pass')

                self.server.update_game_state(event=data)
                self.server.broadcast_game_state_update()

    def finish(self):
        print(f'Disconnecting client with address: {self.client_address}!')
        self.server.remove_client(self)
        super().finish()


class Server(socketserver.ThreadingTCPServer):

    """ Handle TCP connections and all Player Events to update and broadcast the Game state """

    def __init__(self, request_handler_class):
        self.PORT = 10000
        self.BUFFERSIZE = 4096
        super().__init__(('localhost', self.PORT), request_handler_class)
        self.clients = set()

        # Player connections:
        self.player_count = 0
        self.players = {}

        # Game State:
        self.GS = GameState(MAX_PLAYERS)

    def add_client(self, client):
        self.clients.add(client)

    def broadcast_game_state_update(self):
        print(f' >>>> Broadcasting: to {tuple(self.clients)}')
        for client in tuple(self.clients):
            client.send_game_state(self.GS.to_bytes(self.players))
            print('sent')
            print

    def remove_client(self, client):
        self.clients.remove(client)

    def start_game(self):
        self.GS.started = True
        self.broadcast_game_state_update()

    def update_game_state(self, event):
        self.GS.update(event=event)


def main():
    server = Server(RequestHandler)
    server.serve_forever()
    return 0


if __name__ == '__main__':
    main()
