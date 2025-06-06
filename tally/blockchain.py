# tally/blockchain.py
import time, json, hashlib
from .transaction import Transaction
from .ledger import Ledger

DIFFICULTY = 3

class Block:
    def __init__(self, index, prev_hash, txs, timestamp=None, nonce=0, hash=None):
        self.index = index
        self.prev_hash = prev_hash
        self.txs = txs  # list of Transaction objects
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.hash = hash

    def to_dict(self):
        return {
            'index': self.index,
            'prev_hash': self.prev_hash,
            'txs': [tx.to_dict() for tx in self.txs],
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, d):
        txs = [Transaction.from_dict(txd) for txd in d['txs']]
        return cls(d['index'], d['prev_hash'], txs, d['timestamp'], d['nonce'], d['hash'])

    def compute_hash(self):
        block_str = json.dumps({
            'index': self.index,
            'prev_hash': self.prev_hash,
            'txs': [tx.to_dict() for tx in self.txs],
            'timestamp': self.timestamp,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()

def mine_block(block, difficulty=DIFFICULTY):
    prefix = '0' * difficulty
    while True:
        h = block.compute_hash()
        if h.startswith(prefix):
            block.hash = h
            return block
        block.nonce += 1

def verify_block(block, prev_hash, parent_ledger, difficulty=DIFFICULTY):
    if block.prev_hash != prev_hash:
        print("[!] Invalid prev_hash!"); return False
    if not block.hash or not block.hash.startswith('0' * difficulty):
        print("[!] Invalid PoW!"); return False
    ledger_copy = parent_ledger.clone()
    for tx in block.txs:
        if not ledger_copy.execute_transaction(tx):
            print("[!] Invalid transaction in block!"); return False
    return True

def adjust_difficulty(blocks, target_block_time=5, window=100):
    if len(blocks) < window + 1:
        return DIFFICULTY
    actual_time = blocks[-1].timestamp - blocks[-window-1].timestamp
    actual_per_block = actual_time / window
    adjustment = actual_per_block / target_block_time
    new_difficulty = DIFFICULTY * adjustment
    # Clamp to max/min change
    max_change = 2
    new_difficulty = max(DIFFICULTY / max_change, min(DIFFICULTY * max_change, new_difficulty))
    return int(new_difficulty)

# Genesis block creation
GENESIS_BLOCK = {
    'index': 0,
    'prev_hash': '0' * 64,
    'txs': [],
    'timestamp': 1710000000,
    'nonce': 0,
}

def make_genesis_block():
    b = Block(
        GENESIS_BLOCK['index'],
        GENESIS_BLOCK['prev_hash'],
        [],
        GENESIS_BLOCK['timestamp'],
        GENESIS_BLOCK['nonce']
    )
    b.hash = b.compute_hash()
    return b