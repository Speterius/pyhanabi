from socket import socket, AF_INET, SOCK_STREAM
import pickle
import names
import packets


class Client:
    def __init__(self, user_name='DefaultPlayer'):
        self.user_name = user_name
        self.server_address = ('localhost', 10000)

        self.BUFFERSIZE = 2048
        self.sock = socket(AF_INET, SOCK_STREAM)

        self.connected = False
        self.player_id = 999

    def connect_to_server(self):

        print(f'Attempting connection with user name: {self.user_name}')
        self.sock.connect(self.server_address)

        con_attempt = packets.ConnectionAttempt(self.user_name)
        self.sock.send(con_attempt.to_bytes())

        data = self.sock.recv(4096)

        if data:
            data = packets.load(data)

        print(data)

    def receive_packet(self):
        try:
            data = self.sock.recv(4096)
            if not len(data):
                return False
            return pickle.loads(data)
        except:
            return False


def main():

    client = Client(user_name=names.get_first_name())

    client.connect_to_server()

    return 0


if __name__ == '__main__':
    main()