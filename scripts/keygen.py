# scripts/keygen.py
from tally.crypto import gen_keypair

priv, pub, addr = gen_keypair()
print("Address:\n", addr)
# Optionally, print private key PEM (do not share with others!)