import arcade
import names
import packets
from game_window import GameWindow
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM


class Client:

    """ Handles TCP connection to the game Server. After a connection handshake:
    -> Starts a thread that listens to game state updates and communicates with the GUI. """

    def __init__(self, user_name='DefaultPlayerName'):
        self.user_name = user_name
        self.server_address = ('localhost', 10000)

        self.BUFFERSIZE = 4096
        self.sock = socket(AF_INET, SOCK_STREAM)

        self.connected = False
        self.player_id = 999

    def connect_to_server(self, game_window: GameWindow, thread_receive_broadcast: Thread):

        print(f'>>>> Attempting connection with user name: {self.user_name}')
        self.sock.connect(self.server_address)

        # After connecting: attempt a connection handshake to sync string user_names and integer player_id
        con_attempt = packets.ConnectionAttempt(self.user_name)
        self.sock.send(con_attempt.to_bytes())

        # Wait for receiving a confirmation
        data = self.sock.recv(self.BUFFERSIZE)
        if data:
            data = packets.load(data)

        # If confirmation received, start the thread that listens to server updates
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

        """ This is run as a separate thread to listen to game state updates from the server.
        The state updates are forwarded to the game GUI. """

        while True:
            data = self.sock.recv(self.BUFFERSIZE)

            if not data:
                continue

            data = packets.load(data)

            if type(data) is packets.GameStateUpdate:
                data.keys_to_ints()
                game_window.update_game_state(data)
            else:
                print(f'Received not GameStateUpdate broadcast with type: {type(data)}')

    def send_game_event(self, event):

        """ Forwards a player event to the game server. """

        self.sock.send(event)


def main():

    # Instantaiate client and game GUI objects:
    client = Client(user_name=names.get_first_name())
    game_window = GameWindow(client=client)

    # Communicate with server on separate threads:
    thread_receive = Thread(target=client.receive_game_state_broadcast, args=(game_window, ), daemon=True)
    thread_connect = Thread(target=client.connect_to_server, args=(game_window, thread_receive), daemon=True)

    # The receive thread will be started once the connect thread is successful.
    thread_connect.start()

    # Run the arcade game engine
    arcade.run()

    return 0


if __name__ == '__main__':
    main()
