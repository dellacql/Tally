import pytest
from tally.crypto import gen_keypair
from tally.transaction import Transaction

def test_transaction_sign_and_verify():
    priv, pub, addr = gen_keypair()
    tx = Transaction(addr, addr, 0.1, 0)
    tx.sign(priv)
    assert tx.verify_signature()