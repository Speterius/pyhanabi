import socketserver
import packets


class RequestHandler(socketserver.BaseRequestHandler):
    def setup(self):
        print(f'Connecting client with address: {self.client_address}.')

    def handle(self):
        while True:
            # Receive a data packet and decode it:
            data = self.request.recv(self.server.BUFFERSIZE)

            if not data:
                continue

            # Decode the data packet and convert back to a DataPacket class
            data = packets.load(data)

            # If the data packet is a packets.ConnectionAttempt:
            if type(data) is packets.ConnectionAttempt:

                    response = packets.ConnectionConfirmed(True, data.user_name, 5)
                    self.request.send(response.to_bytes())

            elif type(data) in packets.get_events():
                pass

    def finish(self):
        print(f'Disconnecting client with address: {self.client_address}!')


class Server(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, request_handler):
        super().__init__(server_address, request_handler)

        self.BUFFERSIZE = 4096
        self.players = {}


def main():
    server = Server(('localhost', 10000), RequestHandler)
    server.serve_forever()
    return 0


if __name__ == '__main__':
    main()
