from socket import socket, AF_INET, SOCK_STREAM
import names
import packets
from threading import Thread
from game_window import GameWindow
import arcade


class Client:
    def __init__(self, user_name='DefaultPlayer'):
        self.user_name = user_name
        self.server_address = ('localhost', 10000)

        self.BUFFERSIZE = 4096
        self.sock = socket(AF_INET, SOCK_STREAM)

        self.connected = False
        self.player_id = 999

    def connect_to_server(self, game_window: GameWindow, thread_receive_broadcast: Thread):

        print(f'>>>> Attempting connection with user name: {self.user_name}')
        self.sock.connect(self.server_address)

        con_attempt = packets.ConnectionAttempt(self.user_name)
        self.sock.send(con_attempt.to_bytes())

        data = self.sock.recv(self.BUFFERSIZE)

        if data:
            data = packets.load(data)

        if type(data) is packets.ConnectionConfirmed and data.confirmed:
            self.connected = True
            self.player_id = data.player_id

            game_window.player_id = data.player_id
            game_window.connection = True
            game_window.player_name = data.user_name

            print('>>>> Connection to server successful. Starting broadcast receive thread.')
            thread_receive_broadcast.start()

        else:
            print('Connection denied.')

    def receive_game_state_broadcast(self, game_window):
        while True:
            data = self.sock.recv(self.BUFFERSIZE)

            if not data:
                continue

            data = packets.load(data)

            if type(data) is packets.GameStateUpdate:
                print(data)
                game_window.update_game_state(data)
            else:
                print(f'receiving non-GameState broadcast with type: {type(data)}')


def main():

    client = Client(user_name=names.get_first_name())

    game_window = GameWindow(client=client)

    # Communicate with server on a separate thread:
    thread_receive = Thread(target=client.receive_game_state_broadcast, args=(game_window, ), daemon=True)
    thread_connect = Thread(target=client.connect_to_server, args=(game_window, thread_receive), daemon=True)

    thread_connect.start()

    # Run the arcade gameEngine
    arcade.run()

    return 0


if __name__ == '__main__':
    main()