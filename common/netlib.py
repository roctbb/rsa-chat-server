import struct
from common.byteslib import to_bytes, from_bytes
from common.rsalib import decrypt, encrypt

def receive_n(conn, n):
    data = b""

    while len(data) < n:
        data += conn.recv(n)

    return data

def send_bytes(conn, data):
    size = len(data)
    byte_size = struct.pack('<L', size)
    conn.send(byte_size)
    conn.send(data)

def receive_bytes(conn):
    byte_n = receive_n(conn, 4)
    n = struct.unpack('<L', byte_n)[0]
    return receive_n(conn, n)

def send_blocks(conn, blocks):
    n_blocks = len(blocks)
    byte_n_blocks = struct.pack('<L', n_blocks)
    conn.send(byte_n_blocks)

    for block in blocks:
        send_bytes(conn, block)

def receive_blocks(conn):
    block_count = receive_n(conn, 4)
    block_count = struct.unpack('<L', block_count)[0]

    result = []
    for i in range(block_count):
        result.append(receive_bytes(conn))

    return result

def encrypt_and_send(conn, data, key):
    blocks = encrypt(data, key)
    return send_blocks(conn, blocks)

def receive_and_decrypt(conn, key):
    data = receive_blocks(conn)
    return decrypt(data, key)


