import socket
import pickle
from data_packets import ConnectionAttempt, ConnectionState, User, GameState, PlayerEvent

PORT = 10000
BUFFERSIZE = 4096


class Server:
    def __init__(self):
        self.max_users = 4
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('localhost', PORT)
        self.s.bind(self.address)

        self.running = True     # Server Status

        self.client_sockets = []
        self.users = []

        self.GS = GameState(len(self.users), self.users, started=False, current_turn=None)

    def receive_message(self, client_socket):
        try:
            data = client_socket.recv(BUFFERSIZE)
            if not len(data):
                return False
            return pickle.loads(data)
        except:
            return False

    def update_game_state(self, player_event):

        pass

    def main(self):
        # Accept connections until we have 4:
        while len(self.users) < self.max_users:
            print("Server waiting for new connections...")
            self.s.listen()
            client_socket, client_address = self.s.accept()

            print('>>>> Connection attempt by:', client_address)
            print('>>>> Waiting for user data...')

            data = self.receive_message(client_socket)

            if type(data) == ConnectionAttempt:
                new_user = User(client_address[0], client_address[1], data.user_name, data.user_id)
                self.client_sockets.append(client_socket)
                self.users.append(new_user)
                print(f"New User: {new_user} added.")
                c = ConnectionState(confirmed_user=True, user_data=new_user)
                client_socket.send(pickle.dumps(c))
                print('Sent the confirmation.')

            self.GS.users = self.users
            self.GS.user_count = len(self.users)
            for c_s in self.client_sockets:
                c_s.send(pickle.dumps(self.GS))

        print("I have all 4 connections: Let's start the game")
        self.GS.started = True
        turn = 0
        while self.running:
            self.GS.current_turn = self.users[turn]
            # Let everyone know whose turn it is.
            for c_s in self.client_sockets:
                c_s.send(pickle.dumps(self.GS))

            # Listen to the guy whose turn it is.
            # data = self.receive_message(self.users[turn].client_socket)
            input('Enter anything to move on >>')
            # if data == PlayerEvent:
            #    self.update_game_state(data)

            turn += 1
            if turn > 3:
                turn = 0


if __name__ == '__main__':
    server = Server()
    server.main()