import socket

from client.config import PUBLIC_KEY, PRIVATE_KEY
from common import netlib, rsalib
from common import byteslib
import json

sock = socket.socket()
sock.connect(('127.0.0.1', 9090))

e = byteslib.from_bytes(netlib.receive_bytes(sock))
n = byteslib.from_bytes(netlib.receive_bytes(sock))

KEY = (e, n)

print("Server key is", KEY)

self_e, self_n = PUBLIC_KEY
netlib.send_bytes(sock, byteslib.to_bytes(self_e))
netlib.send_bytes(sock, byteslib.to_bytes(self_n))


print("Auth...")

cmd = {
    "cmd": "register",
    "login": "test"
}
netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)

print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

cmd = {
    "cmd": "get_users"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# message
cmd = {
    "cmd": "send_message",
    "user": "roctbb",
    "content": "heh"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# get messages
# message
cmd = {
    "cmd": "get_messages",
    "user": "roctbb",
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# log out
cmd = {
    "cmd": "goodbye"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
sock.close()
