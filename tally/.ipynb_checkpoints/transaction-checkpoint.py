# tally/transaction.py
from decimal import Decimal
import json
from .crypto import load_public_key

class Transaction:
    def __init__(self, sender_addr, recipient_addr, amount, nonce, fee=Decimal("0.0001"), new_account_addr=None, signature=None):
        self.sender_addr = sender_addr
        self.recipient_addr = recipient_addr
        self.amount = Decimal(str(amount))
        self.nonce = nonce
        self.fee = Decimal(str(fee))
        self.new_account_addr = new_account_addr
        self.signature = signature

    def to_dict(self):
        return {
            'sender_addr': self.sender_addr,
            'recipient_addr': self.recipient_addr,
            'amount': str(self.amount),
            'nonce': self.nonce,
            'new_account_addr': self.new_account_addr,
            'signature': self.signature.hex() if self.signature else None
        }

    @classmethod
    def from_dict(cls, d):
        sig = bytes.fromhex(d['signature']) if d['signature'] else None
        return cls(
            d['sender_addr'],
            d['recipient_addr'],
            d['amount'],
            d['nonce'],
            Decimal(d.get('fee', "0.0001")),
            d['new_account_addr'],
            sig)

    def sign(self, priv_key):
        self.signature = priv_key.sign(self.message_bytes(), self._sig_algo())

    def verify_signature(self):
        pub_key = load_public_key(self.sender_addr.encode())
        pub_key.verify(self.signature, self.message_bytes(), self._sig_algo())
        return True

    def _sig_algo(self):
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import hashes
        return ec.ECDSA(hashes.SHA256())

    def message_bytes(self):
        import json
        msg = json.dumps({
            'sender_addr': self.sender_addr,
            'recipient_addr': self.recipient_addr,
            'amount': str(self.amount),
            'nonce': self.nonce,
            'fee': str(self.fee),
            'new_account_addr': self.new_account_addr,
        }, sort_keys=True).encode()
        return msg