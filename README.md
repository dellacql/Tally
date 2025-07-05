# Tally Blockchain

**Tally** is a highly-divisible, fixed-supply, fee-only decentralized blockchain and cryptocurrency system. Tally is designed for speed, liquidity, and security, using robust Proof-of-Work (PoW) for Sybil resistance, with every coin created at genesis and strong mathematical integrity. The system supports modular extension to Proof-of-Stake (PoS) with pBFT consensus.

---

## Table of Contents

- [Features](#features)
- [Coin Model and Properties](#coin-model-and-properties)
- [Architecture & Protocol](#architecture--protocol)
- [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Creating the Genesis Block](#creating-the-genesis-block)
    - [Starting the Node](#starting-the-node)
- [Wallet Usage](#wallet-usage)
    - [Creating a Wallet](#creating-a-wallet)
    - [Listing Addresses](#listing-addresses)
    - [Sending a Transaction](#sending-a-transaction)
    - [Checking a Balance](#checking-a-balance)
- [Trading Coins](#trading-coins)
- [Network & Node](#network--node)
    - [Block Verification](#block-verification)
- [Development & Testing](#development--testing)
- [FAQ](#faq)
- [Summary Table of Coin Properties](#summary-table-of-coin-properties)
- [License](#license)

---

## Features

- **Fixed Supply:** All coins (e.g., 1.0, highly divisible) are created at genesis. No mining, no inflation, no burning.
- **Infinite Divisibility:** The coin is implemented as a high-precision decimal, supporting up to 40 decimal places.
- **Fee-Only Mining:** Miners/validators are compensated by transaction fees; no new coin is minted.
- **Proof-of-Work (PoW):** Efficient, dynamically tunable PoW for Sybil resistance. Block rate is set by difficulty, not inflation.
- **Fast Verification:** Block and transaction validation is fast and deterministic.
- **Sybil Resistant:** PoW and minimum transaction fees prevent spam and Sybil attacks.
- **Account-based Model:** Each address is an ECC public key (PEM format); new accounts must be funded at creation.
- **Extensible Modular Codebase:** Node, wallet, networking, and ledger logic are cleanly separated, making future PoS/pBFT upgrades straightforward.
- **Transparent, Auditable Ledger:** Every account and transaction is visible on-chain, total supply invariant is enforced at every state update.

---

## Coin Model and Properties

- **Genesis Allocation:** Upon creation, 100% of Tally’s coin is initialized in the genesis account(s). The sum of all balances will always match the genesis total (e.g., 1.0).
- **No Minting/Burning:** The coin supply is never increased or reduced. No new coins are minted and coins are never destroyed (except for spending as fees).
- **Infinite Divisibility:** Values can be split into arbitrarily small pieces, supporting trillions of users or tiny payments.
- **Account Creation by Division:** New accounts are only created by subdividing an existing balance; every account must be funded at creation.
- **Mathematical Integrity:** The system enforces the invariant:  
  `sum(all account balances) + sum(fees collected) = total genesis supply`
- **Lossless, Auditable Bookkeeping:** The state is always fully auditable and transparent.

---

## Architecture & Protocol

### 1. Overview

Tally operates as a decentralized, account-based blockchain with a fixed, genesis-minted supply. Each account is an ECC keypair. Transactions are authorized by ECDSA signatures and validated for correct nonces and balances.

### 2. Block Structure

- **index:** Block height
- **prev_hash:** Hash of previous block
- **txs:** List of transactions
- **timestamp:** Time of block creation
- **nonce:** PoW nonce
- **hash:** Block hash

### 3. Transaction Structure

- **sender_addr:** Sender's public address (ECC PEM)
- **recipient_addr:** Recipient's address (ECC PEM)
- **amount:** Amount to transfer
- **fee:** Transaction fee (set by sender, must meet minimum)
- **nonce:** Sender's transaction count
- **new_account_addr:** (Optional) Address to create a new account
- **signature:** ECDSA signature

### 4. Consensus & Security

- **Proof-of-Work (PoW):** Each block must have a hash with a set number of leading zeros (difficulty). This prevents trivial spam and ensures Sybil resistance.
- **No Block Reward:** Miners are paid only by fees from included transactions.
- **Block Verification:** Nodes independently verify PoW, parent hash, and all included transactions.
- **Dynamic Difficulty:** Difficulty may be adjusted to maintain target block times.
- **Trusted Account Origination:** Only funded, signed transactions can create new accounts.
- **Future-Proof:** The protocol can be extended to use PoS and pBFT for even higher efficiency and security.

### 5. Transaction Fees

- **Minimum Fee:** All transactions must include at least the minimum fee (prevents spam).
- **Fee Distribution:** All fees in a block go to the miner (credited after block is mined).

---

## Getting Started

### Prerequisites

-   Python 3.7+
-   `pip` package installer
-   A virtual environment (recommended)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <your_repository_url>
    cd Tally_sample
    ```

2.  **Create and activate a virtual environment (recommended):**

    ```bash
    python -m venv venv  # Create
    ```

    *   **Windows:**

        ```bash
        venv\Scripts\activate  # Activate
        ```

    *   **macOS/Linux:**

        ```bash
        source venv/bin/activate  # Activate
        ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Install the project in editable mode:**

    ```bash
    pip install -e .
    ```

### Configuration

*   **(If you have any configuration files or settings that need adjustment, explain them here)**
*   **(Example: Explain how to set initial balances or network parameters.)**

### Creating the Genesis Block

The genesis block defines the initial state of the blockchain. Follow these steps to create it:

1.  **Run the Genesis Block Creation Script:**
   **1.Edit the scripts\\create_genesis.py and modify the values
      You should edit the num_accounts and the initial_balance to the desired number and the amount you would like to start with
      def main():
        num_accounts = 4  # Number of accounts to create
        initial_balance = 100.0  # Initial coins for each account
        balances = create_genesis_balances(num_accounts, initial_balance)

    **This command creates the genesis_balances.json. Ensure this step runs without errors!**

    ```bash
    python scripts/create_genesis.py
    ```

### Starting the Node

The blockchain node is responsible for processing transactions, maintaining the ledger, and participating in the network.

1.  **Run the Node:**

    ```bash
    python -m tally.rpc
    ```

    *   This will start the Flask server, typically on `http://127.0.0.1:5000`.  Keep this running in a separate terminal window.

---

## Wallet Usage

The Tally wallet allows you to manage your addresses, send transactions, and check your balances.

### Creating a Wallet

1.  **Generate a new wallet address:**

    ```bash
    python -m tally_wallet.cli new
    ```

    This will generate a new address and store the private key in the `wallet.keys` file (or the keyring file you specify).

### Listing Addresses

1.  **List all wallet addresses:**

    ```bash
    python -m tally_wallet.cli list
    ```

    This command will display all addresses currently managed by your wallet.

### Checking a Balance

1.  **Check the balance of an address:**

    ```bash
    python -m tally_wallet.cli list
    ```

    This command will connect to the node and query the balance of the specified address.

### Sending a Transaction

1.  **Send a payment:**

    ```bash
    python -m tally_wallet.cli send <from_address> <to_address> <amount> --password <your_password>
    ```

    *   Replace `<from_address>` with the address you are sending from.
    *   Replace `<to_address>` with the recipient's address.
    *   Replace `<amount>` with the amount you want to send.
    *   The `--password` option will prompt you for the password to unlock the sending address (if applicable).

## Trading Coins

To trade coins on the Tally network, follow these steps:

1.  **Ensure the Node is Running:** Make sure your Tally node is running and connected to the network (see [Starting the Node](#starting-the-node)).

2.  **Create and Fund Your Wallet:**
    - Use the [Creating a Wallet](#creating-a-wallet) instructions to generate an address.
    - Transfer tally coins into that wallet
3.  **Get the Recipient's Address:** Obtain the Tally address of the person you want to send coins to.
4.  **Execute the Send Transaction Command:**
   -Make sure to verify that everything is as it should be, then execute the Send Transaction, where you will type in all the desired values

---

## Network & Node

### Block Verification

Nodes independently verify all blocks and transactions to ensure the integrity of the blockchain.

1.  **(Add detailed instructions for verifying blocks, exploring the chain, etc.)**
2.  **(You might include example commands for querying block data.)**

---

## Development & Testing

1.  **(Include instructions on how to run the tests, contribute code, etc.)**

---

## FAQ

1.  **(Include frequently asked questions and troubleshooting tips.)**

---

## Summary Table of Coin Properties

| Property            | Value                                 |
| ------------------- | ------------------------------------- |
| Total Supply        | (Specify Total Supply)                |
| Divisibility        | 40 decimal places                     |
| Consensus Mechanism | Proof-of-Work (PoW)                    |
| Block Reward        | None (Fee-Only Mining)                |
| Minimum Fee         | (Specify Minimum Fee)                 |

---

## License

(Your License Information Here)
