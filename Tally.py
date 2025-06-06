# -*- coding: utf-8 -*-
"""
Created on Fri May 23 16:32:35 2025

@author: Lucian
"""

from decimal import Decimal, getcontext
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature
import time, json

getcontext().prec = 42  # Support 40 decimal places

ACCOUNT_CREATION_FEE = Decimal("0.001")  # fee is burned
MIN_NEW_ACCOUNT_AMOUNT = Decimal("0.0000000001")  # can't create zero balances

def gen_keypair():
    priv = ec.generate_private_key(ec.SECP256R1())
    pub = priv.public_key()
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return priv, pub, pub_pem

class Transaction:
    def __init__(self, sender_addr, recipient_addr, amount, nonce, new_account_addr=None, signature=None):
        self.sender_addr = sender_addr
        self.recipient_addr = recipient_addr
        self.amount = Decimal(str(amount))
        self.nonce = nonce  # integer, incremented per sender per tx
        self.new_account_addr = new_account_addr  # optional
        self.signature = signature  # bytes

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
        return cls(d['sender_addr'], d['recipient_addr'], d['amount'], d['nonce'], d['new_account_addr'], sig)

    def message_bytes(self):
        # Deterministic order
        msg = json.dumps({
            'sender_addr': self.sender_addr,
            'recipient_addr': self.recipient_addr,
            'amount': str(self.amount),
            'nonce': self.nonce,
            'new_account_addr': self.new_account_addr,
        }, sort_keys=True).encode()
        return msg

    def sign(self, priv_key):
        self.signature = priv_key.sign(self.message_bytes(), ec.ECDSA(hashes.SHA256()))

    def verify_signature(self):
        pub_key = serialization.load_pem_public_key(self.sender_addr.encode())
        pub_key.verify(self.signature, self.message_bytes(), ec.ECDSA(hashes.SHA256()))
        return True

class Ledger:
    def __init__(self, initial_balances):
        self.balances = {k: Decimal(str(v)) for k, v in initial_balances.items()}
        self.nonces = {k: 0 for k in self.balances}  # per-address, start at 0
        self.total_supply = sum(self.balances.values())
        self.fee_collected = Decimal("0")

    def pretty_balances(self):
        for k, v in self.balances.items():
            print(f"Short acct {k[:40]}...: {v}")

    def validate_transaction(self, tx: Transaction):
        # 1. Correct Signature
        try:
            tx.verify_signature()
        except InvalidSignature:
            print("[!] Reject: Invalid signature")
            return False
        # 2. Sender exists
        if tx.sender_addr not in self.balances:
            print("[!] Reject: Sender address not found")
            return False
        # 3. Nonce check
        expected_nonce = self.nonces.get(tx.sender_addr, 0)
        if tx.nonce != expected_nonce:
            print(f"[!] Reject: Bad nonce. Got {tx.nonce}, expected {expected_nonce}")
            return False
        # 4. Enough balance
        total_cost = tx.amount
        if tx.new_account_addr:
            total_cost += ACCOUNT_CREATION_FEE
            if tx.amount < MIN_NEW_ACCOUNT_AMOUNT:
                print("[!] Reject: Amount sent for new account too small")
                return False
            if tx.new_account_addr in self.balances:
                print("[!] Reject: New account already exists")
                return False

        if self.balances[tx.sender_addr] < total_cost:
            print("[!] Reject: Insufficient funds including fees")
            return False
        if tx.amount < Decimal("0"):
            print("[!] Reject: Negative send amount")
            return False
        return True

    def execute_transaction(self, tx: Transaction):
        if not self.validate_transaction(tx):
            return False
        total_cost = tx.amount
        if tx.new_account_addr:
            total_cost += ACCOUNT_CREATION_FEE
        self.balances[tx.sender_addr] -= total_cost
        if tx.recipient_addr not in self.balances:
            self.balances[tx.recipient_addr] = Decimal("0")
        self.balances[tx.recipient_addr] += tx.amount
        # NO need to zero out new_account_addr here!
        if tx.new_account_addr and tx.new_account_addr not in self.nonces:
            print(f"[*] New account created: {tx.new_account_addr[:42]}..., by funding from {tx.sender_addr[:42]}...")
            self.nonces[tx.new_account_addr] = 0
        if tx.new_account_addr:
            self.fee_collected += ACCOUNT_CREATION_FEE
        self.nonces[tx.sender_addr] += 1
        current = sum(self.balances.values()) + self.fee_collected
        if abs(current - self.total_supply) > Decimal('1e-30'):
            raise Exception("Supply invariant broken!")
        return True

# ==== MAIN DEMO ====
if __name__ == '__main__':
    print("==Demo start==")
    # 1. Generate 3 accounts
    p1, pub1, addr1 = gen_keypair()
    p2, pub2, addr2 = gen_keypair()
    p3, pub3, addr3 = gen_keypair()
    # fixed initial allocation
    ledger = Ledger({
        addr1: Decimal("0.5"),
        addr2: Decimal("0.3"),
        addr3: Decimal("0.2"),
    })

    print("\nInitial balances:")
    ledger.pretty_balances()

    # 2. Send funds: addr1 --> addr2 (normal txn)
    t1 = Transaction(sender_addr=addr1, recipient_addr=addr2, amount=Decimal("0.07"), nonce=ledger.nonces[addr1])
    t1.sign(p1)
    assert ledger.execute_transaction(t1)
    print("\n[Transaction 1] addr1 sends 0.07 to addr2.")

    # 3. addr1 sends funds, creating new account
    p4, pub4, addr4 = gen_keypair()
    t2 = Transaction(sender_addr=addr1, recipient_addr=addr4, amount=Decimal("0.01"),
                     nonce=ledger.nonces[addr1], new_account_addr=addr4)
    t2.sign(p1)
    ledger.execute_transaction(t2)
    print("[Transaction 2] addr1 creates and funds new account addr4 (0.01) with creation fee.")

    # 4. addr2 attempts a replay attack (BAD TX: reused nonce!)
    t_bad_replay = Transaction(sender_addr=addr1, recipient_addr=addr2, amount=Decimal("0.02"), nonce=0)  # Wrong nonce!
    t_bad_replay.sign(p1)
    if not ledger.execute_transaction(t_bad_replay):
        print("[Transaction 3] (expected failure): Replay attack detected.")

    # 5. addr4 sends funds to addr2 (requires correct nonce etc)
    t3 = Transaction(sender_addr=addr4, recipient_addr=addr2, amount=Decimal("0.005"), nonce=ledger.nonces[addr4])
    t3.sign(p4)
    ledger.execute_transaction(t3)
    print("[Transaction 4] addr4 sends 0.005 to addr2.")

    # 6. addr1 tries to create an account but not enough to cover fee+amount (should fail)
    p5, pub5, addr5 = gen_keypair()
    t_bad = Transaction(sender_addr=addr1, recipient_addr=addr5, amount=Decimal("0.00001"),
                        nonce=ledger.nonces[addr1], new_account_addr=addr5)
    t_bad.sign(p1)
    if not ledger.execute_transaction(t_bad):
        print("[Transaction 5] (expected failure): Too little to create a new account (fails min amount+fee)")

    print("\nFinal balances:")
    ledger.pretty_balances()
    print(f"\nAccount creation fees burned: {ledger.fee_collected}")
    print("\nDemo complete.")