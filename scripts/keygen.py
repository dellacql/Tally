# scripts/keygen.py
from tally.crypto import gen_keypair
import base64

priv, pub, addr = gen_keypair()
print("Address:", addr)

# If you want to print the public key (DER base64):
pubkey_der = pub.public_bytes(
    encoding='DER',
    format='SubjectPublicKeyInfo'
)
print("Public Key (base64 DER):", base64.b64encode(pubkey_der).decode())

# Unencrypted PEM for backup/testing (never share in production!)
privkey_pem = priv.private_bytes(
    encoding='PEM',
    format='PKCS8',
    encryption_algorithm=None   # For prod, use encryption!
).decode()
print("Private Key PEM:\n", privkey_pem)