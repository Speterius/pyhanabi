from socket import socket, AF_INET, SOCK_STREAM
import pickle
from settings import *
from time import sleep
from packets import ConnectionAttempt, ConnectionConfirmed
from game_logic import GameState


class Server:
    def __init__(self):

        # Game state broadcast update rate:
        self.UPDATE_RATE = 5   # Hz
        self.PORT = 10000
        self.BUFFERSIZE = 8192

        # Generate starting GAME STATE:
        self.GS = GameState(MAX_PLAYERS)
        self.changed = True                 # Broadcast message to all players when the the GameState has changed.

        # Set up server socket:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.address = ('localhost', self.PORT)
        self.sock.bind(self.address)

        # Dictionaries to store user data: keys are integers from 0->MAX_PLAYERS
        self.client_sockets_rec = {}        # The sockets the server receives from
        self.client_sockets_push = {}       # The sockets the server broadcasts to.
        self.players = {}                   # Key: INT, Value: 'Name'

        self.listening_to = self.GS.current_player  # INT key to current player

    # Wait until MAX_PLAYERS number of connections are achieved. Collect all user info and respond.
    def accept_connections(self):
        player_id_counter = 0
        while len(self.players.keys()) < MAX_PLAYERS:
            print(f'Waiting for connections...{len(self.players.keys())}/{MAX_PLAYERS}')
            self.sock.listen(4)

            client_sock_rec, client_address = self.sock.accept()
            client_sock_push, _ = self.sock.accept()
            print('>>>> Connection attempt by: ', client_address)

            data = self.receive_packet(client_sock_rec)

            if type(data) is ConnectionAttempt:

                self.players[player_id_counter] = data.user_name
                self.client_sockets_rec[player_id_counter] = client_sock_rec
                self.client_sockets_push[player_id_counter] = client_sock_push

                print(f'>>>> >>>> New User: {data.user_name}')

                confirm = ConnectionConfirmed(confirmed=True,
                                              user_name=self.players[player_id_counter],
                                              player_id=player_id_counter)

                client_sock_push.send(confirm.to_pickle())
                player_id_counter += 1

            for player_id in self.client_sockets_push.keys():
                client_socket = self.client_sockets_push[player_id]
                client_socket.send(self.GS.to_packet(self.players))

    # Listen to a given a client socket and return the received data.
    def receive_packet(self, client_socket):
        try:
            data = client_socket.recv(self.BUFFERSIZE)
            if not len(data):
                return False
            return pickle.loads(data)
        except:
            return False

    # Listen to a given socket for events. Update the game state when an event arrives.
    def receive_events(self):
        print(f"Server has {MAX_PLAYERS} players. Starting Game...")
        self.GS.started = True

        # 0) Initial broadcast of game start:
        sleep(0.5)      # Wait a bit for clients to start their threads.
        self.broadcast_update()
        print(f'Listening to player with id: {self.listening_to} with Name: {self.players[self.listening_to]}')

        while True:
            # 1) Listen to player events:
            try:
                # todo some kind of race condition here
                data = self.receive_packet(self.client_sockets_rec[self.listening_to])
            except KeyError:
                print("Received data:", data, f'from {self.players[self.listening_to]}')

            print("Received data:", data, f'from {self.players[self.listening_to]}')

            if data:

                # 2) Update Game State
                changed = self.GS.update(event=data)

                # 3) If the Game State has changed, broadcast to all players:
                if changed:
                    self.broadcast_update()

                # 4) Switch the socket to listen to:
                self.listening_to = self.client_sockets_rec[self.GS.current_player]

    def broadcast_update(self):
        for player_id, client_socket in self.client_sockets_push.items():
            try:
                client_socket.sendall(self.GS.to_packet(self.players))
            except ConnectionResetError:
                print('Remote socket disconnected. Skipping player.')
            except:
                # todo
                print('Sending GS update failed. Skipping player.')

    # Continously broadcast the game state at a fixed update rate to all players.
    # def broadcast_updates_continuously(self):
    #     print(f"Server has {MAX_PLAYERS} players. Starting Game...")
    #     self.GS.started = True
    #
    #     while True:
    #
    #         for player_id in self.client_sockets_push.keys():
    #             client_socket = self.client_sockets_push[player_id]
    #             try:
    #                 client_socket.sendall(self.GS.to_packet(self.players))
    #             except ConnectionResetError:
    #                 print('Remote socket disconnected. Waiting a bit, then resending packet.')
    #                 sleep(0.5)


def main():
    # Instansiate server:
    server = Server()

    # Wait for connections:
    server.accept_connections()

    # Start game, listen to player events, update game state and broadcast:
    server.receive_events()

    # thread_receive_events = Thread(target=server.receive_events, args=())
    # thread_broadcast_updates = Thread(target=server.broadcast_updates, args=(), daemon=False)
    # thread_receive_events.start()
    # thread_broadcast_updates.start()

    return 0


if __name__ == '__main__':
    main()
