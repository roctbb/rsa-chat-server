import base64
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

receiver = json.loads(answer.decode('utf-8'))['data'][0]

# 3. Отправка сообщения
# 3.1 Отправка сообщения собеседнику

blocks = rsalib.encrypt("Message text".encode('utf-8'), (receiver['open_exponent'], receiver['module']))
base64_blocks = json.dumps(list(map(lambda x: base64.b64encode(x).decode('ascii'), blocks)))

cmd = {
    "cmd": "send_message",
    "user": receiver['login'],
    "content": base64_blocks
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
print("Waiting for answer...")
answer = netlib.receive_and_decrypt(sock, PRIVATE_KEY)
print("Got cmd: ", answer.decode('utf-8'))


# 3.1 Сохранение на сервере копии для себя

blocks = rsalib.encrypt("Message text".encode('utf-8'), PUBLIC_KEY)
base64_blocks = json.dumps(list(map(lambda x: base64.b64encode(x).decode('ascii'), blocks)))

cmd = {
    "cmd": "send_message",
    "user": receiver['login'],
    "content": base64_blocks,
    "self_copy": True
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

messages = json.loads(answer.decode('utf-8')).get('data')
for message in messages:
    base64_blocks = json.loads(message['content'])
    blocks = list(map(lambda x: base64.b64decode(x), base64_blocks))
    text = rsalib.decrypt(blocks, PRIVATE_KEY).decode('utf-8')

    print("{}: {}".format(message['user'], text))

# 5. Отключение
cmd = {
    "cmd": "goodbye"
}

netlib.encrypt_and_send(sock, json.dumps(cmd).encode('utf-8'), KEY)
sock.close()
