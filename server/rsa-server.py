import json
import threading

from common import netlib
from common import byteslib
import socket
from server.config import PUBLIC_KEY, PRIVATE_KEY
from app import app, User, Message, db


def process_client(client, app):
    with app.app_context():
        e, n = PUBLIC_KEY
        netlib.send_bytes(client, byteslib.to_bytes(e))
        netlib.send_bytes(client, byteslib.to_bytes(n))

        e = byteslib.from_bytes(netlib.receive_bytes(client))
        n = byteslib.from_bytes(netlib.receive_bytes(client))

        user = User.query.filter_by(open_exponent=str(e), module=str(n)).first()

        CLIENT_KEY = (e, n)

        print("Client key is ", CLIENT_KEY)

        while True:
            cmd = netlib.receive_and_decrypt(client, PRIVATE_KEY).decode('utf-8')

            result = {
                "state": "error",
                "error": "incorrect cmd"
            }

            # no json case
            try:
                data = json.loads(cmd)
                cmd = data['cmd']
            except:
                cmd = 'incorrect'
                result = {
                    "state": "error",
                    "error": "incorrect cmd"
                }

            if cmd == "goodbye":
                result = {
                    "state": "ok",
                    "data": "goodbye"
                }

            elif cmd == "ping":
                result = {
                    "state": "ok",
                    "data": "pong"
                }

            elif not user:
                if cmd == "register":
                    if not data.get('login'):
                        result = {
                            "state": "error",
                            "error": "no login"
                        }

                    elif User.query.filter_by(login=data.get('login')).first():
                        result = {
                            "state": "error",
                            "error": "login exists"
                        }

                    else:

                        db.session.add(User(login=data.get('login'), open_exponent=str(e), module=str(n)))
                        db.session.commit()

                        user = User.query.filter_by(open_exponent=str(e), module=str(n)).first()

                        result = {
                            "state": "ok",
                            "data": "welcome"
                        }
                else:
                    result = {
                        "state": "error",
                        "error": "no auth"
                    }
            else:
                if cmd == "register":
                    result = {
                        "state": "error",
                        "error": "already registered",
                        "login": user.login
                    }

                elif cmd == "get_users":
                    users = []

                    for user in User.query.all():
                        users.append({
                            "login": user.login,
                            "open_exponent": int(user.open_exponent),
                            "module": int(user.module)
                        })

                    result = {
                        "state": "ok",
                        "data": users
                    }

                elif cmd == "get_messages":
                    if not data.get('user'):
                        result = {
                            "state": "error",
                            "error": "no user"
                        }
                    elif not User.query.filter_by(login=data.get('user')).first():
                        result = {
                            "state": "error",
                            "error": "no such user"
                        }
                    else:
                        interlocutor = User.query.filter_by(login=data.get('user')).first()
                        messages = []

                        for message in Message.query.filter(
                                ((Message.sender == user.login) & (Message.receiver == interlocutor.login)) | (
                                        (Message.receiver == user.login) & (
                                        Message.sender == interlocutor.login))).order_by(Message.created_on).all():
                            messages.append({
                                "created_at": message.created_on.isoformat(),
                                "content": message.content
                            })

                        result = {
                            "state": "ok",
                            "data": messages
                        }
                elif cmd == "send_message":
                    if not data.get('user') or not data.get('content'):
                        result = {
                            "state": "error",
                            "error": "no user or content"
                        }
                    elif not User.query.filter_by(login=data.get('user')).first():
                        result = {
                            "state": "error",
                            "error": "no such user"
                        }
                    else:
                        interlocutor = User.query.filter_by(login=data.get('user')).first()
                        db.session.add(
                            Message(sender=user.login, receiver=interlocutor.login, content=data.get('content')))
                        db.session.commit()

                        result = {
                            "state": "ok",
                            "data": "sent"
                        }

            netlib.encrypt_and_send(client, json.dumps(result).encode('utf-8'), CLIENT_KEY)

            if cmd == "goodbye":
                print('Disconnected: ', addr)
                client.close()
                break

            continue


clients = []

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(1)

print("Waiting for connections...")

while True:
    conn, addr = sock.accept()
    print('Connected: ', addr)

    thread = threading.Thread(target=process_client, args=(conn, app))
    thread.start()
