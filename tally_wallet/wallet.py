# tally_wallet/wallet.py
from tally_wallet.keyring import Keyring
from tally_wallet.txbuilder import TransactionBuilder

class TallyWallet:
    def __init__(self, keyring_file='wallet.keys'):
        self.keyring = Keyring(keyring_file)
        self.tx_builder = TransactionBuilder(self.keyring)

    def new_account(self, password=None):
        print("Creating new account...")  # debug
        addr = self.keyring.create_new_key(password)
        print(f"New address generated: {addr}")
        return addr
    
    def get_private_key(self, address, password=None):
        return self.keyring.get_private_key(address, password)

    def list_accounts(self):
        return self.keyring.list_addresses()

    def get_balance(self, address, node_rpc):
        # node_rpc: object for talking to a running node, or REST endpoint
        # THIS IS A PLACEHOLDER, you won't use this directly with the new CLI
        return node_rpc.get_balance(address)