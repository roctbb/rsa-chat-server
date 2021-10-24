from common.rsalib import generate_keys

public, private = generate_keys()

print("PUBLIC_KEY =", public)
print("PRIVATE_KEY =", private)