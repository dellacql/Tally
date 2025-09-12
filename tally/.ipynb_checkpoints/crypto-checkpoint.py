# tally/crypto.py
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def gen_keypair():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return priv, pub, pub_pem

def load_public_key(pem_bytes):
    return serialization.load_pem_public_key(pem_bytes)

def gen_ecc_keypair_raw():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    return priv, pub

def pubkey_bytes(pub):
    return pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def pubkey_from_bytes(b):
    return serialization.load_pem_public_key(b)

def derive_shared_key(priv, peer_pub):
    shared_secret = priv.exchange(ec.ECDH(), peer_pub)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b'blockchain-handshake').derive(shared_secret)

def encrypt_message(key, data):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce + ct

def decrypt_message(key, ct):
    aesgcm = AESGCM(key)
    nonce = ct[:12]
    return aesgcm.decrypt(nonce, ct[12:], None)