# tally_wallet/keyring.py
import os
import json
from tally.crypto import gen_keypair
from cryptography.hazmat.primitives import serialization

class Keyring:
    def __init__(self, keyring_file):
        self.file = keyring_file
        self._load()

    def _load(self):
        if os.path.exists(self.file):
            with open(self.file, 'r') as f:
                self.keys = json.load(f)
        else:
            self.keys = {}

    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.keys, f)

    def create_new_key(self, password=None):
        # TODO: use password to encrypt private key
        priv, pub, addr = gen_keypair()
        self.keys[addr] = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
            ).decode()
        self.save()
        return addr

    def list_addresses(self):
        return list(self.keys.keys())

    def get_private_key(self, addr, password=None):
        # TODO: decrypt with password if encrypted
        from cryptography.hazmat.primitives import serialization
        pem = self.keys[addr].encode()
        return serialization.load_pem_private_key(pem, password=None)