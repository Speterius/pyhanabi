from socket import socket, AF_INET, SOCK_STREAM
import pickle
from threading import Thread

from settings import *
from data_packets import ConnectionAttempt, ConnectionConfirmed
from game_logic import GameState, Event


class Server:
    def __init__(self):

        # Game state broadcast update rate:
        self.UPDATE_RATE = 5   # Hz
        self.PORT = 10000
        self.BUFFERSIZE = 4096

        # Generate starting GAME STATE:
        self.GS = GameState(MAX_PLAYERS)
        self.running = True

        # Set up server socket:
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.address = ('localhost', self.PORT)
        self.sock.bind(self.address)

        # Dictionaries to store user data: keys are integers from 0->MAX_PLAYERS
        self.client_sockets_rec = {}        # The sockets the server receives from
        self.client_sockets_push = {}       # The sockets the serbver broadcasts to.
        self.players = {}                   # Key: INT, Value: 'Name'

        self.listening_to = None            # INT key to current player

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

            if data.type() is ConnectionAttempt:

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
        while True:
            data = self.receive_packet(self.listening_to)

            if data.type() is Event:
                self.GS.update(event=data)

                self.listening_to = self.client_sockets[self.GS.current_player]

    # Continously broadcast the game state at a fixed update rate to all players.
    def broadcast_updates(self):
        print(f"Server has {MAX_PLAYERS} players. Starting Game...")
        self.GS.started = True

        while self.running:
            for player_id in self.client_sockets_push.keys():
                client_socket = self.client_sockets_push[player_id]
                client_socket.send(self.GS.to_packet(self.players))


def main():
    server = Server()
    server.accept_connections()

    thread_receive_events = Thread(target=server.receive_events(), daemon=True)
    thread_broadcast_updates = Thread(target=server.broadcast_updates(), daemon=True)

    thread_receive_events.start()
    thread_broadcast_updates.start()


if __name__ == '__main__':
    main()