# tally/node.py
import threading, time
from decimal import Decimal
from .crypto import gen_keypair, gen_ecc_keypair_raw
from .ledger import Ledger
from .blockchain import make_genesis_block, mine_block, Block, verify_block
from .transaction import Transaction
from .network import run_secure_server, connect_and_send_block

def run_demo():
    print("=== Tally Blockchain Demo Starting ===")

    # 1. Setup keys and genesis
    p1, pub1, addr1 = gen_keypair()
    p2, pub2, addr2 = gen_keypair()
    p3, pub3, addr3 = gen_keypair()
    print(f"Account 1 created: {addr1[:40]}...")
    print(f"Account 2 created: {addr2[:40]}...")
    print(f"Account 3 created: {addr3[:40]}...")

    genesis_balances = {addr1: Decimal("0.5"), addr2: Decimal("0.3"), addr3: Decimal("0.2")}
    ledger = Ledger(genesis_balances)
    print("\nGenesis balances:")
    ledger.pretty_balances()
    genesis_block = make_genesis_block()
    blockchain = [genesis_block]

    # 2. Start secure server in another thread
    net_priv, net_pub = gen_ecc_keypair_raw()
    threading.Thread(
        target=run_secure_server,
        args=(net_priv, net_pub, '127.0.0.1', 5008, ledger, blockchain),
        daemon=True
    ).start()

    # 3. Build transactions and mine a block
    time.sleep(1)
    MIN_TX_FEE = Decimal("0.0001")
    t1 = Transaction(
        sender_addr=addr1,
        recipient_addr=addr2,
        amount=Decimal("0.07"),
        nonce=ledger.nonces[addr1],
        fee=MIN_TX_FEE
    )
    t1.sign(p1)
    p4, pub4, addr4 = gen_keypair()
    print(f"New account (Account 4) to be created: {addr4[:40]}...")

    t2 = Transaction(
        sender_addr=addr1,
        recipient_addr=addr4,
        amount=Decimal("0.01"),
        nonce=ledger.nonces[addr1]+1,
        fee=MIN_TX_FEE,
        new_account_addr=addr4
    )
    t2.sign(p1)

    txs_block1 = [t1, t2]
    temp_ledger = ledger.clone()
    print("\n--- Transactions to be included in next block ---")
    for tx in txs_block1:
        print(f"  From: {tx.sender_addr[:10]}... To: {tx.recipient_addr[:10]}... "
              f"Amount: {tx.amount} Fee: {tx.fee} Nonce: {tx.nonce} "
              f"{'(New Account)' if tx.new_account_addr else ''}")
        assert temp_ledger.execute_transaction(tx)

    block1 = Block(1, genesis_block.hash, txs_block1)
    block1 = mine_block(block1)
    print(f"\n[Block 1 Mined] Index: {block1.index}, Hash: {block1.hash[:16]}...")

    # 4. Securely propagate the block to the server (simulate network propagation)
    client_priv, client_pub = gen_ecc_keypair_raw()
    connect_and_send_block(client_priv, client_pub, '127.0.0.1', 5008, block1)
    time.sleep(2)

    print("\n--- Final Balances After Block ---")
    ledger.pretty_balances()
    print(f"Total supply (should not change): {ledger.total_supply}")

    # 5. Verification: Check the block is valid on a fresh ledger
    fresh_ledger = Ledger(genesis_balances)
    if verify_block(block1, genesis_block.hash, fresh_ledger):
        print("\n[Verification] Block 1 verified successfully on a new node/ledger!")
    else:
        print("\n[Verification] Block 1 verification FAILED!")

    print("\n--- Blockchain Summary ---")
    for blk in blockchain:
        print(f"Block {blk.index} | Hash: {blk.hash[:12]}... | Prev: {blk.prev_hash[:12]}...")
        for tx in blk.txs:
            print(f"   Tx: {tx.sender_addr[:10]}... -> {tx.recipient_addr[:10]}... "
                  f"Amount: {tx.amount}, Fee: {tx.fee}, Nonce: {tx.nonce}")
    print("QTY_VERIFY",ledger.total_supply)
    print("\n=== End of Demo ===")

if __name__ == '__main__':
    run_demo()