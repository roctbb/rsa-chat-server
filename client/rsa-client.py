import socket

from client.config import PUBLIC_KEY, PRIVATE_KEY
from common import netlib, rsalib
from common import byteslib

sock = socket.socket()
sock.connect(('127.0.0.1', 9090))

e = byteslib.from_bytes(netlib.receive_bytes(sock))
n = byteslib.from_bytes(netlib.receive_bytes(sock))

KEY = (e, n)

print("Server key is", KEY)

self_e, self_n = PUBLIC_KEY
netlib.send_bytes(sock, byteslib.to_bytes(self_e))
netlib.send_bytes(sock, byteslib.to_bytes(self_n))


for i in range(10):
    print("Sending ping...")
    crypted_cmd = rsalib.encrypt("ping".encode('utf-8'), KEY)
    print("Sending blocks", crypted_cmd)
    netlib.send_blocks(sock, crypted_cmd)

    print("Waiting for answer...")
    crypted_cmd = netlib.receive_blocks(sock)
    cmd = rsalib.decrypt(crypted_cmd, PRIVATE_KEY).decode('utf-8')
    print("Got cmd: ", cmd)

netlib.send_blocks(sock, rsalib.encrypt("end".encode('utf-8'), KEY))
sock.close()