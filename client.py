import arcade
import names
import pickle
from socket import socket, AF_INET, SOCK_STREAM
import sys
from time import sleep
from threading import Thread
from data_packets import ConnectionAttempt, ConnectionConfirmed, GameStateUpdate
from game_logic import Event
from game_window import GameWindow


class Client:
    def __init__(self, user_name='Player123'):
        self.user_name = user_name
        self.server_address = ('localhost', 10000)

        self.BUFFERSIZE = 4096
        self.PLAYER_EVENT_UPDATE_F = 10  # Hz

        self.sock_rec = socket(AF_INET, SOCK_STREAM)       # Receive updates
        self.sock_push = socket(AF_INET, SOCK_STREAM)      # Broadcast event

        self.connected = False
        self.player_id = 999

    def receive_packet(self):
        try:
            data, server = self.sock_rec.recvfrom(self.BUFFERSIZE)
            if not len(data):
                return False
            return pickle.loads(data)
        except:
            return False

    def send_packet(self, data):
        data = pickle.dumps(data)
        try:
            self.sock_push.sendall(data)
        except ConnectionResetError:
            print('Server socket is down. Closing game.')
            sys.exit()

    def wait_for_server(self):
        # print('Server is not available. Waiting for server...')
        waiting = True
        while waiting:
            try:
                self.sock_rec.connect(self.server_address)
                waiting = False
            except:
                pass
                sleep(0.2)

    def connect_to_server(self, game_window, thread_receive):
        print(f'>>>> Attempting connection with player name: {self.user_name}...')

        while not self.connected:
            try:
                self.sock_push.connect(self.server_address)
            except ConnectionRefusedError:
                self.wait_for_server()
            finally:
                self.sock_rec.connect(self.server_address)

            con_attempt = pickle.dumps(ConnectionAttempt(self.user_name))
            self.sock_push.sendall(con_attempt)

            data = self.receive_packet()
            print('received packed:', type(data))

            if type(data) is ConnectionConfirmed and data.confirmed:
                self.connected = True
                self.player_id = data.player_id

                # Tell the GUI the player integer ID -> KEY for players dictionary
                game_window.player_id = data.player_id
                game_window.connection = True
                game_window.player_name = data.user_name

                print('>>>> Connection to server successful. Starting Threads:')
                print('Game window think the connection is:', game_window.connection)
                thread_receive.start()
            else:
                print('Connection is not confirmed.')

        # Handle Server Connection Failures
        # .
        # .
        # /todo

    def receive_game_state_broadcast(self, game_window):
        while self.connected:
            data = self.receive_packet()
            if not data:
                sleep(0.1)
            else:
                if type(data) is GameStateUpdate:
                    game_window.update_game_state(data)
                else:
                    print(f'receiving non-GameState broadcast with type: {type(data)}')

    def send_game_event(self, event):
        # if type(event) is Event:
        try:
            print('Sending Game event:', event)
            self.sock_push.sendall(event.to_packet())
        except ConnectionResetError:
            print('Server socket is down.')
            self.wait_for_server()


def main():
    testing = True

    if not testing:
        name = input('Enter username (max 12 letters):  >')
        while len(name) > 12:
            name = input('Enter username (max 12 letters): >')
    else:
        name = names.get_first_name()

    client = Client(user_name=name)
    game_window = GameWindow(client=client)

    # Receive from server on a separate thread:
    thread_receive = Thread(target=client.receive_game_state_broadcast, args=(game_window, ), daemon=True)
    thread_connect = Thread(target=client.connect_to_server, args=(game_window, thread_receive), daemon=True)

    thread_connect.start()

    # Run the arcade gameEngine
    arcade.run()
    return 0


if __name__ == '__main__':
    main()
