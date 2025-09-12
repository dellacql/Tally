# scripts/start_node.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tally.node import run_node
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a Tally blockchain node.")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='The host address to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='The port to listen on (default: 5000)')
    args = parser.parse_args()
    run_node(host=args.host, port=args.port)