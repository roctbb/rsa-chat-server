import socket

from example_client.config import PUBLIC_KEY, PRIVATE_KEY
from common import netlib, rsalib
from common import byteslib
import json

# 0. соединение с сервером
sock = socket.socket()
sock.connect(('127.0.0.1', 9090))

# 1. обмен ключами
# 1.1 получение открытого ключа сервера
e = byteslib.from_bytes(netlib.receive_bytes(sock))
n = byteslib.from_bytes(netlib.receive_bytes(sock))

KEY = (e, n)

print("Server key is", KEY)

# 1.2 Отправка своего открытого ключа
self_e, self_n = PUBLIC_KEY
netlib.send_bytes(sock, byteslib.to_bytes(self_e))
netlib.send_bytes(sock, byteslib.to_bytes(self_n))

# 1. Регистрация ника (необходимо только при первом подключении)
print("Auth...")

cmd = {
    "cmd": "register",
    "login": "test"
}
netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)

print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# 2. Получение списка пользователей с сервера
cmd = {
    "cmd": "get_users"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# 3. Отправка сообщения
cmd = {
    "cmd": "send_message",
    "user": "roctbb",
    "content": "heh"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# 4. Получение списка сообщений
cmd = {
    "cmd": "get_messages",
    "user": "roctbb",
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))

# 5. Отключение
cmd = {
    "cmd": "goodbye"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
sock.close()
