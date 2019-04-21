import socket
import pickle
from time import sleep
from settings import *

from data_packets import ConnectionAttempt, ConnectionState, User, GameState, PlayerEvent
import threading

from game_data import Deck

PORT = 10000
BUFFERSIZE = 4096


class Server:
    def __init__(self):
        self.UPDATE_RATE = 10   # Hz
        self.max_users = MAX_USERS
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('localhost', PORT)
        self.s.bind(self.address)

        self.running = True     # Server Status

        self.client_sockets_rec = []
        self.client_sockets_push = []
        self.users = []

        self.listening_to = None

        self.GS = GameState(len(self.users), self.users, started=False, current_turn=None, player_cards={})

        self.turn = 0  # Turn index loops through users.

    @staticmethod
    def receive_message(client_socket):
        try:
            data = client_socket.recv(BUFFERSIZE)
            if not len(data):
                return False
            return pickle.loads(data)
        except:
            return False

    def update_game_state(self, player_event):
        # Set the next player to be their turn:
        if player_event.next_turn:
            self.turn += 1
            if self.turn >= len(self.users):
                self.turn = 0

            self.GS.current_turn = self.users[self.turn]  # Set current player in the GameState
            self.listening_to = self.client_sockets_push[self.turn]  # The socket to receive player updates from

        # Card logic
        if player_event.info:
            print('lost info point')
            self.GS.lose_info()
        elif player_event.place:
            print(f'placed card: {player_event.card_placed}')
        elif player_event.burn:
            print(f'burned card: {player_event.card_burned}')
            self.GS.add_info()

    def receive_player_events(self):
        while True:
            if self.listening_to is not None:
                data = self.receive_message(self.listening_to)
                if type(data) == PlayerEvent:
                    self.update_game_state(data)

    def accept_connections(self):
        while len(self.users) < self.max_users:
            print(f"Waiting for connections...{len(self.users)}/{self.max_users}")
            self.s.listen(4)
            client_sock_rec, client_address = self.s.accept()
            client_sock_push, _ = self.s.accept()
            print('>>>> Connection attempt by:', client_address)
            data = self.receive_message(client_sock_rec)

            if type(data) == ConnectionAttempt:
                new_user = User(client_address[0], client_address[1], data.user_name, data.user_id)
                self.client_sockets_rec.append(client_sock_rec)
                self.client_sockets_push.append(client_sock_push)
                self.users.append(new_user)
                print(f">>>> >>>> New User: {new_user.name} added.")
                c = ConnectionState(confirmed_user=True, user_data=new_user)
                client_sock_rec.send(pickle.dumps(c))

            self.GS.users = self.users
            self.GS.user_count = len(self.users)
            for c_s in self.client_sockets_rec:
                c_s.send(pickle.dumps(self.GS))

    def run(self):
        # Accept connections until we have 4:
        print(f"Server has {self.max_users} players. Starting Game...")

        # Initialize the game:
        self.GS.started = True

        # Make Deck of cards:
        deck = Deck()
        player_cards = {}

        for u in self.users:
            player_cards[u.user_id] = [deck.pull_card() for _ in range(4)]

        self.GS.player_cards = player_cards
        self.GS.current_turn = self.users[self.turn]
        self.listening_to = self.client_sockets_push[self.turn]

        while self.running:
            for c_s in self.client_sockets_rec:  # Let everyone know whose turn it is.
                c_s.send(pickle.dumps(self.GS))
                sleep(1./self.UPDATE_RATE)


def main():
    server = Server()
    server.accept_connections()  # Accept connections until we have 4:

    thread_updates = threading.Thread(target=server.receive_player_events, args=(), daemon=True)
    thread_updates.start()

    server.run()


if __name__ == '__main__':
    main()
