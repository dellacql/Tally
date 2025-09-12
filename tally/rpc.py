# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 15:45:36 2025

@author: Lucian
"""

from flask import Flask, request, jsonify
from tally.ledger import Ledger
from tally.blockchain import Block, make_genesis_block, mine_block, verify_block
from tally.transaction import Transaction

from decimal import Decimal

app = Flask(__name__)

# ===== Simple In-Memory Node State =====

# All this should be persisted in real apps!
genesis_balances = {}  # TODO: Replace with your chain's real genesis
try:
    with open('genesis_balances.json') as f:
        import json
        genesis_balances = json.load(f)
    print("Genesis loaded from file.")
except Exception:
    print("Genesis balances not found; expect trouble if you didn't set them manually!")

ledger = Ledger({k: Decimal(str(v)) for k, v in genesis_balances.items()})
blockchain = [make_genesis_block()]
mempool = []

# ===== REST API =====

@app.route("/balance/<address>")
def balance(address):
    amt = str(ledger.balances.get(address, 0))
    return jsonify({"balance": amt})

@app.route("/nonce/<address>")
def nonce(address):
    n = int(ledger.nonces.get(address, 0))
    return jsonify({"nonce": n})

@app.route("/sendtx", methods=['POST'])
def sendtx():
    global blockchain, ledger, mempool 
    tx_data = request.json
    try:
        tx = Transaction.from_dict(tx_data)
        # Validate signature and basics
        if ledger.validate_transaction(tx):
            mempool.append(tx)
            return jsonify({"accepted": True, "error": None})
        else:
            return jsonify({"accepted": False, "error": "invalid"})
    except Exception as e:
        return jsonify({"accepted": False, "error": str(e)})

@app.route("/mine", methods=['POST'])
def mine():
    global blockchain, ledger, mempool  # <--- MUST be first in the function!
    if not mempool:
        return jsonify({"mined": False, "error": "no tx"})
    temp_ledger = ledger.clone()
    txs = []
    for tx in mempool:
        if temp_ledger.execute_transaction(tx):
            txs.append(tx)
    if not txs:
        return jsonify({"mined": False, "error": "no valid tx"})

    lastblock = blockchain[-1]
    newblk = Block(
        index=lastblock.index + 1,
        prev_hash=lastblock.hash,
        txs=txs
    )
    newblk = mine_block(newblk)
    blockchain.append(newblk)
    for tx in txs:
        ledger.execute_transaction(tx)
    mempool = []
    return jsonify({"mined": True, "block": newblk.to_dict()})

@app.route("/block/<int:bidx>")
def block_by_idx(bidx):
    if 0 <= bidx < len(blockchain):
        return jsonify(blockchain[bidx].to_dict())
    return jsonify({"error": "out of range"})

@app.route("/mempool")
def get_mempool():
    return jsonify([tx.to_dict() for tx in mempool])

@app.route("/")
def home():
    return "TallyNode API"

if __name__ == "__main__":
    app.run(debug=True, port=5000)