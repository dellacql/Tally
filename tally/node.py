# In tally/node.py
from cryptography.hazmat.primitives import ec
from flask import Flask, request, jsonify
from tally.transaction import Transaction
from decimal import Decimal
from tally.crypto import gen_keypair, gen_ecc_keypair_raw # Import gen_keypair
from tally.ledger import Ledger # Import Ledger
from tally.blockchain import make_genesis_block, Block, verify_block # Import make_genesis_block, Block
import threading
from .network import run_secure_server  # Import run_secure_server

app = Flask(__name__)

# Global variables for blockchain, ledger, and keys (initialized in run_node)
blockchain = None
ledger = None
net_priv = None
net_pub = None
addr = None
priv = None
node_state = {} # Declare outside run_node() so that it is always global, not overwritten on runs.

NODE_INDEX = 0  # Represents the index of our node.
# pBFT Constants
PBFT_NODES = 4  # Total number of nodes (example)
PBFT_FAULTY_NODES = 1 # Allow one fault node to have consensus.
# Consensus algorithm parameter.
VALID_PREPARES_AND_COMMITS_TO_VALIDATE = PBFT_NODES - PBFT_FAULTY_NODES


def run_node(host='127.0.0.1', port=5000):
    global blockchain, ledger, net_priv, net_pub, addr, priv, node_state # Declare global variables
    # Initialize keys and genesis block (same as in run_demo)
    priv, pub, addr = gen_keypair()
    net_priv, net_pub = gen_ecc_keypair_raw()

    genesis_balances = {addr: Decimal("1000")}  # Initialize genesis balance
    ledger = Ledger(genesis_balances)
    genesis_block = make_genesis_block()
    blockchain = [genesis_block]
    assign_leader()

    # pBFT Constants

    node_state = { # Set state to be only is_leader.
        'is_leader': False,
        'leader_index': 0,
        'prepared': False,
        'committed': False,
        'prepare_votes': [], # List of nodes that have voted prepare
        'commit_votes': [],  # List of nodes that have voted commit
        'current_block': None
    }

    # Start secure server in a thread
    threading.Thread(
        target=run_secure_server,
        args=(net_priv, net_pub, '127.0.0.1', 5008, ledger, blockchain),
        daemon=True
    ).start()

    print(f"Node started with address: {addr[:40]}...")

    app.run(host=host, port=port, debug=True, use_reloader=False)

def is_leader():
    global node_state
    return node_state['leader_index'] == NODE_INDEX

def assign_leader():
    global node_state
    # Determine the leader based on the round robin algorithm.
    # This will rotate through our addresses.
    node_state['leader_index'] = (len(blockchain) + 1) % PBFT_NODES

# Consensus algorithm.
def pbft_consensus(block):
    global ledger, blockchain, node_state
    # Verify PoW, Verify block (verify_block already does this and checks txns).
    if verify_block(block, blockchain[-1].hash, ledger):
        # 1. Check if we have the number of pre-commits and commits.
        node_state['prepared'] = False
        node_state['committed'] = False
        node_state['prepare_votes'] = []
        node_state['commit_votes'] = []
        node_state['current_block'] = block
        # Start consensus.
        start_pbft_consensus_messages(block)
    else:
        print("Consensus failed: Invalid block.")

def start_pbft_consensus_messages(block):
    # Step 1) - Send pre-prepare message to all nodes,
    message = {'type': 'pre-prepare', 'block': block.to_dict()}
    broadcast_message(message) # Send message to all other nodes.

def handle_pre_prepare_message(block_data):
    global node_state, blockchain, ledger
    block = Block.from_dict(block_data)

    # Step 1: Consensus - Once we get this we pre-prepare the block and start the voting.
    if verify_block(block, blockchain[-1].hash, ledger):
        # Now we Prepare a vote that a Prepare vote and send it to everyone.
        message = {'type': 'prepare', 'block': block.to_dict()}
        broadcast_message(message)
    else:
        print("Consensus failed: Invalid block received.")


def handle_prepare_message(block_data):
    global node_state, blockchain, ledger, addr

    block = Block.from_dict(block_data)

    # Check if we have not already voted in prepare.
    if addr not in node_state['prepare_votes'] and node_state['current_block'] == block:

        if verify_block(block, blockchain[-1].hash, ledger):
            node_state['prepare_votes'].append(addr)

            # Step 2: Commit a vote to all nodes,
            if len(node_state['prepare_votes']) >= VALID_PREPARES_AND_COMMITS_TO_VALIDATE:
                node_state['prepared'] = True

                # Now we Commit a vote and send it to everyone.
                message = {'type': 'commit', 'block': block.to_dict()}
                broadcast_message(message)
        else:
            print("Consensus failed: Invalid block received.")
    else:
        print("Consensus: already committed or invalid")



def handle_commit_message(block_data):
    global node_state, blockchain, ledger, addr

    block = Block.from_dict(block_data)

    # Check if we have not already voted in commit.
    if addr not in node_state['commit_votes'] and node_state['current_block'] == block:

        if verify_block(block, blockchain[-1].hash, ledger):
            node_state['commit_votes'].append(addr)

            # Step 3: Apply to blockchain - If we have enough commits we can validate.
            if len(node_state['commit_votes']) >= VALID_PREPARES_AND_COMMITS_TO_VALIDATE and node_state['prepared']:

                node_state['committed'] = True

                for tx in block.txs:
                    ledger.execute_transaction(tx)
                blockchain.append(block)
                print(f"Block #{block.index} appended!")
        else:
            print("Consensus failed: Invalid block received.")
    else:
        print("Consensus: already committed or invalid")



def broadcast_message(message):
    # This is a placeholder.  Replace with your actual broadcasting logic.
    # Iterate over known peers and send the transaction.
    # Use the secure communication channel (encrypt_message, connect_and_send_block).
    # You'll need a list of peers that the node maintains.
    print("Broadcasting message:", message['type'])  # For debugging
    # broadcast_transaction(tx) # Implement the broadcast_transaction function
    pass  # Replace with actual implementation


# ---- START OF RPC MESSAGES ----
@app.route('/pre-prepare', methods=['POST'])
def pre_prepare():
    data = request.get_json()
    handle_pre_prepare_message(data['block'])
    return jsonify({'message': 'pre-prepare message received'}), 200

@app.route('/prepare', methods=['POST'])
def prepare():
    data = request.get_json()
    handle_prepare_message(data['block'])
    return jsonify({'message': 'prepare message received'}), 200

@app.route('/commit', methods=['POST'])
def commit():
     data = request.get_json()
     handle_commit_message(data['block'])
     return jsonify({'message': 'commit message received'}), 200

@app.route('/transaction', methods=['POST'])
def new_transaction():
    global ledger, blockchain  # Access the global variables
    tx_data = request.get_json()
    try:
        tx = Transaction.from_dict(tx_data)
        if ledger.validate_transaction(tx):
            # Broadcast transaction (implement your broadcast logic here)
            print("Broadcasting transaction:", tx_data)  # For debugging
            # broadcast_transaction(tx) # Implement the broadcast_transaction function
            return jsonify({'message': 'Transaction received and broadcasted'}), 202
        else:
            return jsonify({'error': 'Invalid transaction'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Invalid transaction data'}), 400

@app.route('/block', methods=['POST'])
def new_block():
    global ledger, blockchain # Access the global variables
    block_data = request.get_json()
    try:
        block = Block.from_dict(block_data)
        if verify_block(block, blockchain[-1].hash, ledger):
            for tx in block.txs:
                ledger.execute_transaction(tx)
            blockchain.append(block)
            print(f"Block #{block.index} added via RPC!")
            return jsonify({'message': 'Block accepted'}), 201
        else:
            return jsonify({'error': 'Invalid block'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Invalid block data'}), 400

@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    global ledger # Access the global variable
    balance = ledger.balances.get(address, Decimal("0"))
    return jsonify({'address': address, 'balance': str(balance)}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    global blockchain # Access the global variable
    chain_data = [block.to_dict() for block in blockchain]
    return jsonify(chain_data), 200

@app.route('/address', methods=['GET'])
def get_address():
    global addr # Access the global variable
    return jsonify({'address': addr}), 200


def broadcast_transaction(tx):
    # This is a placeholder.  Replace with your actual broadcasting logic.
    # Iterate over known peers and send the transaction.
    # Use the secure communication channel (encrypt_message, connect_and_send_block).
    # You'll need a list of peers that the node maintains.
    pass  # Replace with actual implementation


if __name__ == '__main__':
    run_node()