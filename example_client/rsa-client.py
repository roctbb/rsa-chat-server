import base64
import socket
import json

from common import netlib, rsalib
from common import byteslib

# публичный и приватный ключ клиента
from example_client.config import PUBLIC_KEY, PRIVATE_KEY


# Вспомогательные функции
# шифрование и отправка команды на сервер, получение и декодирование ответа
def send_command(cmd, KEY, connection):
    # dict -> JSON string -> bytes
    netlib.encrypt_and_send(connection, json.dumps(cmd).encode('utf-8'), KEY)
    print("Sending ", cmd)

    answer = netlib.receive_and_decrypt(connection, PRIVATE_KEY)
    print("Answer is", answer.decode('utf-8'))

    # bytes -> JSON string -> dict
    return json.loads(answer.decode('utf-8'))

# шифрование текста и кодирование в JSON список base64 блоков
def prepare_text(text, KEY):
    # string -> bytes -> List[bytes]
    blocks = rsalib.encrypt(text.encode('utf-8'), KEY)

    # List[bytes] -> List[base64 string] -> JSON string
    return json.dumps(list(map(lambda x: base64.b64encode(x).decode('ascii'), blocks)))

# расфшифровка и превращение обратно в текст JSON списка из base64 блоков
def decode_text(text, KEY):
    # JSON string -> List[base64 string]
    base64_blocks = json.loads(text)
    # List[base64 string] -> List[bytes]
    blocks = list(map(lambda x: base64.b64decode(x), base64_blocks))
    # List[bytes] -> bytes -> string
    return rsalib.decrypt(blocks, KEY).decode('utf-8')

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
send_command({
    "cmd": "register",
    "login": "test"
}, KEY, sock)

# 2. Получение списка пользователей с сервера

users = send_command({
    "cmd": "get_users"
}, KEY, sock).get('data')

# первый пользователь в списке (но его может не быть)
receiver = users[0]

# 3. Отправка сообщения
# 3.1 Отправка сообщения собеседнику

# текст шифруется ключем получателя и кодируется в список base64 фрагментов
# обратно этот текст с сервера уже не получить - ключ для расшифровки неизвестен
encrypted_content = prepare_text("Hello world!", (receiver['open_exponent'], receiver['module']))

send_command({
    "cmd": "send_message",
    "user": receiver['login'],
    "content": encrypted_content
}, KEY, sock)


# 3.1 Сохранение на сервере копии для себя
# на этот раз текст шифруется уже нашим открытым ключем - его можно будет забрать обратно и расшифровать
encrypted_content = prepare_text("Hello world!", PUBLIC_KEY)

send_command({
    "cmd": "send_message",
    "user": receiver['login'],
    "content": encrypted_content,
    "self_copy": True
}, KEY, sock)


# 4. Получение списка сообщений - с пользователем roctbb
messages = send_command({
    "cmd": "get_messages",
    "user": "roctbb",
}, KEY, sock).get('data')

for message in messages:
    # декордируем список из base64 строк, расшифровываем и склеиваем его, а затем - превращаем в текст
    text = decode_text(message['content'], PRIVATE_KEY)
    print("{}: {}".format(message['user'], text))

# 5. Отключение
send_command({
    "cmd": "goodbye"
}, KEY, sock)

sock.close()
