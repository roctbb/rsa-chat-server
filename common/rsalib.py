import random

from common.byteslib import to_bytes, from_bytes


def bezout(a, b):
    '''An implementation of extended Euclidean algorithm.
    Returns integer x, y and gcd(a, b) for Bezout equation:
        ax + by = gcd(a, b).
    '''
    x, xx, y, yy = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x, xx = xx, x - xx*q
        y, yy = yy, y - yy*q
    return (x, y, a)

def modular_pow(a, b, m):
    result = 1

    while b != 0:
        if b % 2 == 0:
            a = (a * a) % m
            b = b // 2
        else:
            result = (result * a) % m
            b = b - 1

    return result

def generate_prime(start, end):
    while True:
        n = random.randint(start, end)

        is_prime = True

        for i in range(20):
            a = random.randint(3, n - 1)

            if modular_pow(a, n - 1, n) != 1:
                is_prime = False
                break

        if is_prime:
            return n

def generate_e(phi):
    while True:
        candidate = generate_prime(3, 10000)

        if phi % candidate != 0:
            break
    return candidate

def generate_keys(keysize=1024):
    p = generate_prime(2**(keysize-1), 2**(keysize)-1)
    q = generate_prime(2**(keysize-1), 2**(keysize)-1)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = generate_e(phi)

    d, k, g = bezout(e, phi)

    while d <= 0:
        d = d + phi

    return (e, n), (d, n)

def encrypt(B, key):
    e, n = key

    key_size = (len(to_bytes(n)) - 1) // 2
    print(key_size)

    blocks = []

    while len(B) > key_size:
        blocks.append(B[:key_size])
        B = B[key_size:]
    blocks.append(B[:key_size])

    blocks = list(map(lambda x: to_bytes(modular_pow(from_bytes(x), e, n)), blocks))

    return blocks

def decrypt(data, key):
    result = []
    for block in data:
        x = from_bytes(block)
        e, n = key
        result.append(to_bytes(modular_pow(x, e, n)))

    return b"".join(result)

