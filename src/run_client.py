import arcade
from client.client import Client
from game.game_window import GameWindow
from threading import Thread


def main():

    # Instantaiate client and game GUI:
    client = Client(user_name="Tyrone", server_adress=("localhost", 10000))
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
