# tally_wallet/keyring.py
import sys
print(sys.path)
import os
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric import ec
import base64
import base58  # pip install base58
import hashlib

class Keyring:
    def __init__(self, keyring_file='wallet.keys'):
        self.keyring_file = keyring_file
        self.keys = self._load_keys()

    def _load_keys(self):
        if os.path.exists(self.keyring_file):
            try:
                with open(self.keyring_file, 'r') as f:
                    content = f.read()
                    if content:
                        return json.loads(content)
                    else:
                        return {}
            except json.JSONDecodeError:
                print("Error: Keyring file is corrupted.  Starting with an empty keyring.")
                return {}
        else:
            return {}

    def _save_keys(self):
        with open(self.keyring_file, 'w') as f:
            json.dump(self.keys, f)

    def create_new_key(self, password=None):
        priv = ec.generate_private_key(ec.SECP256R1(), default_backend())
        pub = priv.public_key()

        pubkey_der = pub.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        pubkey_b64 = base64.b64encode(pubkey_der).decode()

        address = self._public_key_to_address(pub)

        key_entry = {
            "public_key": pubkey_b64
        }

        if password:
            encrypted_private_key = self._encrypt_private_key(priv, password)
            key_entry["encrypted_private_key"] = encrypted_private_key
            key_entry["is_encrypted"] = True
        else:
            private_key_pem = priv.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).decode()
            key_entry["private_key"] = private_key_pem
            key_entry["is_encrypted"] = False

        self.keys[address] = key_entry
        self._save_keys()
        return address

    def get_private_key(self, address, password=None):
        if address not in self.keys:
            raise ValueError(f"Address {address} not found in keyring.")
        key_data = self.keys[address]
        if key_data.get('is_encrypted'):
            if not password:
                raise ValueError("This key is encrypted.  A password is required.")
            encrypted_private_key = key_data['encrypted_private_key']
            private_key = self._decrypt_private_key(encrypted_private_key, password)
            return private_key
        else:
            private_key_pem = key_data.get('private_key')
            if not private_key_pem:
                raise ValueError(f"No private key found for address {address}")
            return serialization.load_pem_private_key(
                private_key_pem.encode(),
                password=None,
                backend=default_backend()
            )

    def list_addresses(self):
        return list(self.keys.keys())

    def _encrypt_private_key(self, private_key, password):
        """
        Encrypts the private key using AES-GCM.
        Stores (salt || nonce || ciphertext || tag) as base64.
        """
        password_bytes = password.encode('utf-8')
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        key = kdf.derive(password_bytes)
        nonce = os.urandom(12)
        # Prepare plaintext
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        # AES-GCM with explicit tag management
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(private_key_bytes) + encryptor.finalize()
        tag = encryptor.tag
        # Store as salt || nonce || ciphertext || tag
        return base64.b64encode(salt + nonce + ciphertext + tag).decode('utf-8')

    def _decrypt_private_key(self, encrypted_private_key, password):
        """
        Decrypts the private key using AES-GCM.
        Expects (salt || nonce || ciphertext || tag), all as one base64 blob.
        """
        decoded = base64.b64decode(encrypted_private_key)
        salt = decoded[:16]
        nonce = decoded[16:28]
        tag = decoded[-16:]
        ciphertext = decoded[28:-16]
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        key = kdf.derive(password_bytes)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        try:
            private_key_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        except InvalidTag:
            raise ValueError("Invalid password or corrupted data.")
        return serialization.load_pem_private_key(
            private_key_bytes,
            password=None,
            backend=default_backend()
        )

    def _public_key_to_address(self, public_key):
        pubkey_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        sha = hashlib.sha256(pubkey_bytes).digest()
        ripe = hashlib.new('ripemd160', sha).digest()
        address = base58.b58encode(ripe).decode()
        return address