import pickle
import socket
from random import randint, choice
from threading import Thread
import arcade
from data_packets import ConnectionAttempt, ConnectionState, GameState
from ClientWindow import GameWindow
from time import sleep
from string import ascii_letters
import sys


class Client:
    def __init__(self, user_name='Player123'):
        self.name = user_name
        self.user_id = randint(1, 10000)
        self.server_address = ('localhost', 10000)

        self.BUFFERSIZE = 8192
        self.PLAYER_EVENT_UPDATE_F = 15  # Hz

        self.sock_rec = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_push = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connected = False
        self.user_data = 0

    def receive_message(self):
        try:
            data, server = self.sock_rec.recvfrom(self.BUFFERSIZE)
            if not len(data):
                return False
            return pickle.loads(data)
        except:
            return False

    def send_message(self, data):
        data = pickle.dumps(data)
        try:
            self.sock_push.sendall(data)
        except ConnectionResetError:
            print('Server socket is down. Closing game.')
            sys.exit()

    def wait_for_server(self):
        print('Server is not available. Waiting for server...')
        waiting = True
        while waiting:
            try:
                self.sock_rec.connect(self.server_address)
                waiting = False
            except:
                pass
                sleep(0.2)

    def connect_to_server(self, window, thread_recieve, thread_send):
        # Connect and send data:
        print(f'>>>> Attempting connection with player name: {self.name}...')

        try:
            self.sock_rec.connect(self.server_address)
        except ConnectionRefusedError:
            self.wait_for_server()
        finally:
            self.sock_push.connect(self.server_address)

        con_attempt = pickle.dumps(ConnectionAttempt(self.user_id, self.name))
        self.sock_rec.sendall(con_attempt)

        # Wait for confirmation:
        data = self.receive_message()
        # If we get good confirmation: become connected
        if type(data) == ConnectionState:
            if data.confirmed_user:
                self.connected = True
                self.user_data = data.user_data
                window.update_user_data(data.user_data)
                window.connection = True
                print('>>>> Connection to server successful. Starting Threads:')
                thread_recieve.start()
                thread_send.start()
            else:
                print('I am not confirmed.')
        else:
            print('I dont know what packet I just got.')

    def receive_updates(self, window):
        while self.connected:
            data = self.receive_message()
            if not data:
                sleep(0.1)
            elif type(data) == GameState:
                window.update_game_state(data)

        self.sock_rec.close()

    def send_player_events(self, window):
        while True:
            PE = window.get_player_event()
            self.send_message(PE)
            window.reset_player_event()
            sleep(1./self.PLAYER_EVENT_UPDATE_F)


def main():
    TESTING = True

    # Player Name:
    if not TESTING:
        name = input('Enter username (max 10 letters): >')
        while len(name) > 8:
            name = input('Enter username (max 10 letters): >')
    else:
        name = ''.join(choice(ascii_letters) for _ in range(9))

    client = Client(user_name=name)
    window = GameWindow()
    # client.connect_to_server(window)

    # Receive from server on a separate thread:
    thread_recieve = Thread(target=client.receive_updates, args=(window,), daemon=True)
    thread_send = Thread(target=client.send_player_events, args=(window,), daemon=True)
    thread_connect = Thread(target=client.connect_to_server, args=(window, thread_recieve, thread_send), daemon=True)

    thread_connect.start()

    # Run the arcade GameEngine
    arcade.run()
    return 0


if __name__ == '__main__':
    main()
