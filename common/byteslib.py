
def to_bytes(number):
    binary = bin(number)
    result = int(binary, 2).to_bytes((len(binary) + 7) // 8, byteorder='big')

    if result.startswith(b'\x00'):
        result = result[1:]

    return result

def from_bytes(data):
    result = int.from_bytes(data, "big")
    return result
