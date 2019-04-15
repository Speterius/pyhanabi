import pickle
import socket
import random
import threading
import arcade
from data_packets import ConnectionAttempt, User, ConnectionState, GameState, PlayerEvent
from ClientWindow import ClientWindow


def communicate_with_server(window):
    # Set up client socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)

    # Connection ID:
    name = input('Enter username: >')
    while len(name) > 8:
        name = input('Enter username (max 10 letters): >')
    assert type(name) == str
    pd = ConnectionAttempt(random.randint(1, 10000), name)
    msg = pickle.dumps(pd)

    is_connected = False

    # Connect to server via user name and user id:
    s.connect(server_address)
    s.sendall(msg)

    # # Wait for a confirmation response
    print('Waiting For confirmation:...')
    data, server = s.recvfrom(8192)
    data = pickle.loads(data)

    if type(data) == ConnectionState:
        print(data.confirmed_user)
        if data.confirmed_user:
            is_connected = True
            window.update_user_data(data.user_data)
        else:
            is_connected = False

    if is_connected:
        while True:
            print('>>>> Waiting for gamestate updates')
            data, server = s.recvfrom(8192)
            data = pickle.loads(data)
            if type(data) == GameState:
                window.update_game_state(data)
    else:
        print('Shutting Down client.')


def main():
    # GUI Window:
    window = ClientWindow()

    # Server Communication on a separate thread:
    thread = threading.Thread(target=communicate_with_server, args=(window,), daemon=True)
    thread.start()

    # Run the arcade GameEngine
    arcade.run()
    return 0


if __name__ == '__main__':
    main()
