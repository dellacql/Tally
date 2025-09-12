# Tally Blockchain Project
Tally is a minimal blockchain implementation with wallet support, transaction signing, a simple CLI, and a Flask-based node server. This project is ideal for learning or prototyping a basic UTXO-less (account-based) ledger.
________________________________________
## Features
** Password-Encypted Wallets: Generate and safely store multiple accounts; private keys are encrypted with user-provided passwords using robust AES-GCM.
** Short, CLI-Friendly Addresses: Wallet addresses are short, URL-safe, and based on a hash of the user's public key (not raw PEM/DER).
** Blockchain Node: A Flask server runs the blockchain, processes transactions, and exposes HTTP endpoints (/balance, /nonce, /sendtx, etc.).
** Genesis Configuration: Initialize the chain with funded accounts, fully under your control (only those with wallet-stored keys are usable).
** Transaction Creation & Signing: Build and sign transactions with your wallet; signatures are validated by the node using public keys sent in each transaction.
** Mining: Mempool, block mining, and block/hash validation.
** CLI Wallet: Command-line interface supports account creation, listing, sending coins, and more.
** Chain & Block Explorer Endpoints: Query current balances, blocks, and the mempool.
________________________________________
### Quick Start
1. Install Dependencies
pip install -r requirements.txt
** If not present, you need:
pip install cryptography base58 flask click requests
________________________________________
#### 2. Create Your Wallet Account
Each account/password combo is created and encrypted locally (in wallet.keys):
python -m tally_wallet.cli new
** Enter a password when prompted.
** On completion, your CLI will print your new address (a short base58 string).
** Keep your password safe! If you lose it, you can't recover the private key.
________________________________________
#### 3. Prepare Genesis Block
Only addresses for which you have local wallet keys should be funded in genesis!
Create (or overwrite) genesis_balances.json.
You can use the helper script:
python scripts/create_genesis.py
Paste your address (from the previous step) when prompted.
Your address will be funded with 1.0 coins in genesis; you are now the initial "faucet."
________________________________________
#### 4. Start the Blockchain Node
In a new terminal:
python -m tally.rpc
or, if you use a helper script:
python scripts/start_node.py
** The node will read genesis_balances.json and initialize itself.
** You should see output like:
** Genesis loaded from file.
** * Serving Flask app 'rpc'
** * Running on http://127.0.0.1:5000
________________________________________
#### 5. Send Transactions
Use your wallet to send coins from your funded account to any valid address:
python -m tally_wallet.cli send <FROM_ADDR> <TO_ADDR> <AMOUNT>
** Example:
** python -m tally_wallet.cli send 3BotBqmAxEAiUxDuuRUBXeh26WNw rA9xdcnmGLdEfsyBMUqMUp5EXa6 0.25
** Enter your password (for <FROM_ADDR>) when prompted.
** The CLI will report whether the transaction was accepted.
________________________________________
#### 6. Mine Transactions
After sending, transactions enter the node’s mempool.
To mine new blocks (and confirm transactions):
curl -X POST http://127.0.0.1:5000/mine
or send a POST request using any http client.
________________________________________
#### 7. View the Blockchain and Explore
Query balance:
curl http://127.0.0.1:5000/balance/<ADDRESS>
View mempool:
curl http://127.0.0.1:5000/mempool
Get a block by index:
curl http://127.0.0.1:5000/block/<N>
List all wallet addresses:
python -m tally_wallet.cli list
________________________________________
## How it Works — Technical Details
Wallets and Keys
** Each new account is locally protected by a password. Private keys use AES-GCM encryption.
** Wallet addresses are hashes of the public key (RIPEMD160(SHA256(...)) then Base58 encoding).
** Only short, URL-safe addresses are used for CLI and node communication.
## Genesis
** Fund only those addresses for which you control the private keys (using your wallet).
** The node loads balances from genesis_balances.json at launch.
## Transactions & Signatures
** Each transaction carries the public key as a base64-encoded DER.
** The node always verifies signatures against this included public key, not the short address.
** Transaction sender addresses are always short hashes, not PEMs.
## Node Functionality
** /sendtx endpoint adds validated transactions to the mempool.
** /mine endpoint processes the mempool into a new block, appends to the chain, and updates balances.
** All states are currently stored in memory (for demonstration and local testing).
________________________________________
## Features, Security & Limitations
** Encrypted key storage
** Message signing
** Address derivation is one-way and secure
** Password protection is enforced locally
** All communication is via HTTP (insecure, for test/dev only)
** No persistent blockchain state beyond runtime
** No P2P or network consensus — this is a single-node educational chain
________________________________________
## Advanced Topics & Customization
** Add more addresses to genesis_balances.json for multi-party devnet (each party creates their own wallet!)
** Implement/expand mining, difficulty adjustment, or REST documentation.
** Persist chain and wallet states to disk for a longer-lived local chain.
________________________________________
## Troubleshooting
Issue	Solution
"No connection/cannot reach node..."	Start the node first! (python -m tally.rpc)
"Invalid signature"	Ensure CLI and node both include public_key in every transaction, and use it for verification, not the address hash. Field order+encoding in message must match for signing and verification.
"Address not found in keyring"	You can only spend from addresses generated by your wallet.
"Password required / is incorrect"	Enter the correct password chosen at account creation (no recovery if forgotten).
"404 for /transaction"	The correct endpoint is /sendtx, not /transaction. Update your CLI accordingly.
________________________________________
License
This project is for instructional/research use only.
________________________________________
Credits
Built with Flask, cryptography, base58, Click.
________________________________________
Happy hacking!
For questions or contributions, open an issue or pull request.
________________________________________
Example Workflow (Summary)
### 1. Install required packages
pip install -r requirements.txt

### 2. Create an account in your wallet
python -m tally_wallet.cli new

### 3. Create genesis_balances.json with your new address

### 4. Run the node server
python -m tally.rpc

### 5. List wallet addresses
python -m tally_wallet.cli list

### 6. Send some coins!
python -m tally_wallet.cli send <FROM_ADDR> <TO_ADDR> <AMOUNT>

