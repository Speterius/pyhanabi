from .tcp_server import TCPServer
from .request_handler import RequestHandler


def main():
    server = TCPServer(RequestHandler)
    print('Waiting for connections...')
    server.serve_forever()
    return 0


if __name__ == '__main__':
    main()
