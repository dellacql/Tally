# tally_wallet/cli.py
import click
from .wallet import TallyWallet

@click.group()
def cli():
    print("CLI running!")
    pass

@cli.command()
@click.option('--keyring', default='wallet.keys', show_default=True, help='Path to keyring file')
def new(keyring):
    """Generate a new wallet address."""
    wallet = TallyWallet(keyring)
    wallet.new_account()

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
@click.option('--password', prompt=True, hide_input=True)
@click.option('--fee', type=float, default=0.0001)
@click.option('--keyring', default='wallet.keys', show_default=True, help='Path to keyring file')
def send(from_addr, to_addr, amount, password, fee, keyring):
    """Send a payment."""
    wallet = TallyWallet(keyring)
    # TODO: connect to node RPC
    node_rpc = None
    wallet.send(from_addr, to_addr, amount, password, node_rpc, fee)
    
if __name__ == '__main__':
    cli()