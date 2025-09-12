# tally_wallet/txbuilder.py
import requests
from tally.transaction import Transaction
import base64

class TransactionBuilder:
    def __init__(self, keyring):
        self.keyring = keyring

    def build_transaction(self, from_addr, to_addr, amount, fee, password, private_key, node_url='http://127.0.0.1:5000'):
        """
        Build and sign an account-based transaction.
        Fetch the current nonce from the node.
        """
        # Fetch the nonce from the node
        nonce_url = f"{node_url}/nonce/{from_addr}"
        resp = requests.get(nonce_url)
        resp.raise_for_status()
        nonce = resp.json()["nonce"]

        # Build transaction with only the allowed fields
        pubkey_b64 = self.keyring.keys[from_addr]["public_key"]
        tx = Transaction(
            sender_addr=from_addr,
            recipient_addr=to_addr,
            amount=amount,
            nonce=nonce,
            fee=fee,
            public_key=pubkey_b64,
            new_account_addr=None
        )

        tx.sign(private_key)
        return tx