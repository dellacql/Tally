# tally_wallet/txbuilder.py
from tally.transaction import Transaction
from decimal import Decimal

class TransactionBuilder:
    def __init__(self, keyring):
        self.keyring = keyring

    def build_transaction(self, from_addr, to_addr, amount, password=None, fee=Decimal("0.0001"), nonce=None, new_account_addr=None):
        priv = self.keyring.get_private_key(from_addr, password)
        # Nonce should be fetched from node for from_addr
        # Here, we just set it to 0 or require caller to set
        tx = Transaction(
            sender_addr=from_addr,
            recipient_addr=to_addr,
            amount=amount,
            nonce=nonce,
            new_account_addr=new_account_addr
        )
        tx.sign(priv)
        return tx