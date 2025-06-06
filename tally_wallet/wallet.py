# tally_wallet/wallet.py
from .keyring import Keyring
from .txbuilder import TransactionBuilder

class TallyWallet:
    def __init__(self, keyring_file='wallet.keys'):
        self.keyring = Keyring(keyring_file)
        self.tx_builder = TransactionBuilder(self.keyring)

    def new_account(self, password=None):
        print("Creating new account...")  # debug
        addr = self.keyring.create_new_key(password)
        print(f"New address generated: {addr}")
        return addr

    def list_accounts(self):
        return self.keyring.list_addresses()

    def get_balance(self, address, node_rpc):
        # node_rpc: object for talking to a running node, or REST endpoint
        return node_rpc.get_balance(address)
    
    def new(keyring):
        print(f"Creating new address in keyring {keyring}")  # debug
        wallet = TallyWallet(keyring)
        wallet.new_account()

    def send(self, from_addr, to_addr, amount, password, node_rpc, fee=0):
        tx = self.tx_builder.build_transaction(from_addr, to_addr, amount, password, fee)
        txid = node_rpc.send_transaction(tx)
        print(f"Transaction sent, TXID: {txid}")
        return txid