# scripts/fund_account.py
# (Only use on dev/test net, gives coins to an address in genesis or via mining)
import sys
from tally.ledger import Ledger
from tally.crypto import gen_keypair

if len(sys.argv) < 3:
    print("Usage: python scripts/fund_account.py <address> <amount>")
    exit(1)

address = sys.argv[1]
amount = float(sys.argv[2])

# Example: update a genesis balances file or send a funding tx
print(f"Fund {address} with {amount} coins (implement logic!)")