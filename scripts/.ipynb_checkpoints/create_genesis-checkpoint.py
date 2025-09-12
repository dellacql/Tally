# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 14:57:57 2025

@author: Lucian
"""
from cryptography.hazmat.primitives import serialization
import sys
import os
import json
import base64
import json

#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



def main():
    print("First, create your genesis account with your wallet using:")
    print("  python -m tally_wallet.cli new")
    print("You MUST save the address and password!\n")
    addr = input("Paste your wallet-generated address here: ").strip()
    initial_balance = 1.0
    genesis = {addr: initial_balance}
    with open("genesis_balances.json", "w") as f:
        json.dump(genesis, f, indent=2)
    print(f"Genesis balances written to genesis_balances.json.")
    print(f"Funded address: {addr} with {initial_balance} coin.")

if __name__ == "__main__":
    main()