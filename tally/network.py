# tally/network.py
import socket, threading, json
from .crypto import pubkey_from_bytes, pubkey_bytes, derive_shared_key, encrypt_message, decrypt_message

def run_secure_server(priv, pub, host, port, ledger, blockchain):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"[Server] Listening on {host}:{port}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_peer, args=(conn, priv, pub, ledger, blockchain)).start()

def handle_peer(conn, priv, pub, ledger, blockchain):
    try:
        peer_pub_bytes = conn.recv(4096)
        peer_pub = pubkey_from_bytes(peer_pub_bytes)
        conn.sendall(pubkey_bytes(pub))
        shared_key = derive_shared_key(priv, peer_pub)
        print("[Server] Shared key with peer established.")

        while True:
            ct = conn.recv(8192)
            if not ct: break
            msg = decrypt_message(shared_key, ct)
            msgd = json.loads(msg.decode())
            if msgd['type'] == 'block':
                from .blockchain import Block, verify_block
                b = Block.from_dict(msgd['data'])
                print(f"[Server] Received encrypted block: #{b.index} with hash {b.hash[:16]}...")
                if verify_block(b, blockchain[-1].hash, ledger):
                    for tx in b.txs: ledger.execute_transaction(tx)
                    blockchain.append(b)
                    print(f"[Server] Block #{b.index} appended!")
                else:
                    print("[Server] Invalid block received.")
    finally:
        conn.close()

def connect_and_send_block(priv, pub, peer_addr, peer_port, block):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((peer_addr, peer_port))
    s.sendall(pubkey_bytes(pub))
    peer_pub_bytes = s.recv(4096)
    peer_pub = pubkey_from_bytes(peer_pub_bytes)
    shared_key = derive_shared_key(priv, peer_pub)
    print("[Client] Shared key with peer established.")
    msg = {'type': 'block', 'data': block.to_dict()}
    import json
    msg_bytes = json.dumps(msg).encode()
    ct = encrypt_message(shared_key, msg_bytes)
    s.sendall(ct)
    s.close()