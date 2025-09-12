# In tally_wallet/cli.py
# In tally_wallet/cli.py
import click
import requests
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tally_wallet.wallet import TallyWallet  # Changed to absolute import
from tally.transaction import Transaction
from tally.crypto import gen_keypair # added


@click.group()
def cli():
    pass

@cli.command()
@click.option('--keyring', default='wallet.keys', show_default=True, help='Path to keyring file')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password to protect the new account.')
def new(keyring, password):
    """Generate a new wallet address."""
    wallet = TallyWallet(keyring)
    wallet.new_account(password)

@cli.command()
@click.option('--keyring', default='wallet.keys', show_default=True, help='Path to keyring file')
def list(keyring):
    """List all wallet addresses."""
    wallet = TallyWallet(keyring)
    for addr in wallet.list_accounts():
        print(addr)

@cli.command()
@click.argument('from_addr')
@click.argument('to_addr')
@click.argument('amount', type=float)
@click.option('--password', prompt=True, hide_input=True, help='Password to unlock the sending account.')
@click.option('--fee', type=float, default=0.0001)
@click.option('--keyring', default='wallet.keys', show_default=True, help='Path to keyring file')
def send(from_addr, to_addr, amount, fee, keyring, password):
    """Send a payment."""
    wallet = TallyWallet(keyring)
    node_rpc = SimpleNodeRPC('http://127.0.0.1:5000') # Or whatever your node's address is

    #Get the private key for the from address
    try:
        private_key = wallet.get_private_key(from_addr, password)

    except ValueError as e:
        print(f"Error: {e}")
        return #Exit if there is an error getting the private key

    tx = wallet.tx_builder.build_transaction(
        from_addr=from_addr,
        to_addr=to_addr,
        amount=amount,
        password=password, #Make sure the builder receives the password so the wallet unlocks and signs
        fee=fee,
        private_key=private_key # Pass the private key for signing
    )


    txid = node_rpc.send_transaction(tx)
    print(f"Transaction sent, TXID: {txid}")
    return txid

class SimpleNodeRPC:  # A basic class to interact with the node
    def __init__(self, base_url):
        self.base_url = base_url

    def send_transaction(self, tx):
        url = f"{self.base_url}/sendtx"
        headers = {'Content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(tx.to_dict()), headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()  # Return the response as JSON

if __name__ == '__main__':
    cli()