import socket
import pickle
from data_packets import ConnectionAttempt, ConnectionState, User, GameState, PlayerEvent
import threading

PORT = 10000
BUFFERSIZE = 4096


class Server:
    def __init__(self):
        self.max_users = 4
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('localhost', PORT)
        self.s.bind(self.address)

        self.running = True     # Server Status

        self.client_sockets_rec = []
        self.client_sockets_push = []
        self.users = []

        self.listening_to = None

        self.GS = GameState(len(self.users), self.users, started=False, current_turn=None)

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

        pass

    def receive_player_events(self):
        while True:
            if self.listening_to is not None:
                data = self.receive_message(self.listening_to)
                if type(data) == PlayerEvent:
                    if data.info:
                        print('info')
                    elif data.place:
                        print('place')
                    elif data.burn:
                        print('burn')

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
        print("Server has 4 players. Starting Game.")

        # Initialize the game:
        self.GS.started = True
        turn = 0
        while self.running:
            self.GS.current_turn = self.users[turn]             # Set current player in the GameState
            self.listening_to = self.client_sockets_push[turn]  # The socket to receive player updates from

            for c_s in self.client_sockets_rec:  # Let everyone know whose turn it is.
                c_s.send(pickle.dumps(self.GS))

            # Listen to the guy whose turn it is.
            # data = self.receive_message(self.users[turn].client_socket)
            input('Enter anything to move on >>')
            # if data == PlayerEvent:
            #    self.update_game_state(data)

            turn += 1
            if turn > 3:
                turn = 0


def main():
    server = Server()
    server.accept_connections()  # Accept connections until we have 4:

    thread_updates = threading.Thread(target=server.receive_player_events, args=(), daemon=True)
    thread_updates.start()

    server.run()


if __name__ == '__main__':
    main()
