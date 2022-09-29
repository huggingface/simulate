import socket


class Client:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 55001
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect()

    def _connect(self):
        self.socket.connect((self.host, self.port))

    def listen(self, callback):
        chunk_size = 1024
        while True:
            msg_length = int.from_bytes(self.socket.recv(4), "little")
            if msg_length:
                data = ""
                while len(data) < msg_length:
                    data += self.socket.recv(min(chunk_size, msg_length - len(data))).decode()
                callback(data)
                break

    def send_bytes(self, data):
        self.socket.sendall(data)

    def close(self):
        self.socket.close()
