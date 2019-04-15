import pickle
import socket
from data_packets import ConnectionAttempt, User, ConnectionState, \
    GameState, PlayerEvent

# *** Settings ***
MAX_USERS = 4
PORT = 10000
PACKET_SIZE = 4096


class Server:
    def __init__(self):
        # Set up Socket s:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = ('localhost', PORT)
        self.s.bind(self.address)

        # Users
        self.users = []

        # Game State
        self.GS = GameState(users=self.users, started=False)

    def main(self):
        # Wait for received packages:
        #   if playerdata:
        #       update user list
        #   if game event:
        #       update game state
        #   publish right after any even occurrs
        while True:
            data, addr = self.wait_for_incoming_data()
            if type(data) == ConnectionAttempt:
                self.connect_new_users(data, addr)

            if type(data) == PlayerEvent:
                self.update_game_state()

            # Send game state to users:
            for u in self.users:
                self.s.sendto(pickle.dumps(self.GS), (u.IP, u.PORT))
                print(f'Sent GS to {u.name} at port: {u.PORT}')

    def update_game_state(self):
        pass

    def wait_for_incoming_data(self):
        data, address = self.s.recvfrom(PACKET_SIZE)
        data = pickle.loads(data)
        print(f'>>>>Received dataset from {address}.')
        print(f'>>>>Printing Data: {data}.')
        return data, address

    def connect_new_users(self, data, address):
        user_ids = [u.user_id for u in self.users]
        if data.user_id not in user_ids:
            if len(self.users) == MAX_USERS:
                print('Connection Rejected. Reach MAX user count')
                c = ConnectionState(confirmed_user=False, user_data=None)
                self.s.sendto(pickle.dumps(c), address)
                print('>>>>>>>> Sent Rejection')
            elif len(self.users) < MAX_USERS:
                new_user = User(address[0], address[1], data.user_name, data.user_id)
                self.users.append(new_user)
                print(f'New User!! Address book: {self.users}')

                # Confirm Connection:
                c = ConnectionState(confirmed_user=True, user_data=new_user)
                self.s.sendto(pickle.dumps(c), address)
                print('>>>>>>>> Sent Confirmation')
        else:
            print('This guy is already in my addresbook')
            for u in self.users:
                if u.user_id == data.user_id:
                    u.__setattr__('IP', address[0])
                    u.__setattr__('PORT', address[1])
                    u.__setattr__('name', data.user_name)
                    print(u)

        # Update users in the game state
        self.GS.users = self.users


if __name__ == '__main__':
    server = Server()
    server.main()
