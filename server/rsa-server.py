import threading

from common import rsalib
from common import netlib
from common import byteslib
import socket
from server.config import PUBLIC_KEY, PRIVATE_KEY


def process_client(client):
    e, n = PUBLIC_KEY
    netlib.send_bytes(client, byteslib.to_bytes(e))
    netlib.send_bytes(client, byteslib.to_bytes(n))

    e = byteslib.from_bytes(netlib.receive_bytes(client))
    n = byteslib.from_bytes(netlib.receive_bytes(client))

    KEY = (e, n)

    print("Client key is ", KEY)

    while True:
        print("Waiting for cmd...")
        crypted_cmd = netlib.receive_blocks(client)
        print("Got blocks ", crypted_cmd)

        cmd = rsalib.decrypt(crypted_cmd, PRIVATE_KEY).decode('utf-8')

        print("Got cmd: ", cmd)

        if cmd == "end":
            client.close()
            break

        if cmd == "ping":
            netlib.send_blocks(client, rsalib.encrypt("pong".encode('utf-8'), KEY))

        continue


clients = []

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)

print("Waiting for connections...")

while True:
    conn, addr = sock.accept()
    print('Connected: ', addr)

    thread = threading.Thread(target=process_client, args=(conn, ))
    thread.start()




