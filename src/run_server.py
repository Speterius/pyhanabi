from server.tcp_server import TCPServer


def main():
    server = TCPServer(server_address=('localhost', 10000))
    print('Waiting for connections...')
    server.serve_forever()
    return 0


if __name__ == '__main__':
    main()
