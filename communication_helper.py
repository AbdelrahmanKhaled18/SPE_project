from enum import Enum


class Protocol(Enum):
    BYTES = 1
    JSON = 2


PROTOCOL = Protocol.BYTES
SERVER_HOST = "localhost"
SERVER_PORT = 1420


def recvall(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet
    return data
