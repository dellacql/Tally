# Tally Blockchain

**Tally** is a highly-divisible, fixed-supply, fee-only decentralized blockchain designed for speed, liquidity, and security. Tally uses a Proof-of-Work (PoW) protocol with efficient verification and robust Sybil resistance, and all coins are created at genesis—there is no ongoing inflation.

---

## Table of Contents

- [Features](#features)
- [Architecture & Protocol](#architecture--protocol)
- [How to Run the Demo](#how-to-run-the-demo)
- [Wallet Usage](#wallet-usage)
    - [Creating a Wallet](#creating-a-wallet)
    - [Listing Addresses](#listing-addresses)
    - [Sending a Transaction](#sending-a-transaction)
    - [Checking a Balance](#checking-a-balance)
- [Network & Node](#network--node)
    - [Starting the Node](#starting-the-node)
    - [Block Verification](#block-verification)
- [Development & Testing](#development--testing)
- [FAQ](#faq)
- [License](#license)

---

## Features

- **Fixed Supply:** All coins (1.0, highly divisible) are created at genesis. No inflation.
- **Fee-Only Mining:** Miners are compensated via transaction fees; no new coins minted.
- **Proof-of-Work (PoW):** Efficient, dynamically tunable PoW. Mining difficulty governs block rate, not inflation.
- **Fast Verification:** Block and transaction validation is fast and deterministic.
- **Sybil Resistant:** PoW and minimum transaction fees prevent spam and Sybil attacks.
- **Account-based Model:** Each address is a unique ECC public key (PEM format).
- **Extensible Modular Codebase:** Clean separation for node, wallet, networking, and ledger logic.

---

## Architecture & Protocol

### 1. **Overview**

Tally operates as a decentralized, account-based blockchain with a fixed, genesis-minted supply. Each account is an ECC keypair. Transactions are authorized by ECDSA signatures and validated for correct nonces and balances.

### 2. **Block Structure**

- **index**: Block height
- **prev_hash**: Hash of previous block
- **txs**: List of transactions
- **timestamp**: Time of block creation
- **nonce**: PoW nonce
- **hash**: Block hash

### 3. **Transaction Structure**

- **sender_addr**: Sender's public address (ECC PEM)
- **recipient_addr**: Recipient's address (ECC PEM)
- **amount**: Amount to transfer
- **fee**: Transaction fee (set by sender, must meet minimum)
- **nonce**: Sender's transaction count
- **new_account_addr**: (Optional) Address to create a new account
- **signature**: ECDSA signature

### 4. **Consensus & Security**

- **Proof-of-Work (PoW):** Each block must have a hash with a set number of leading zeros (difficulty). This prevents trivial spam and ensures Sybil resistance.
- **No Block Reward:** Miners are paid only by fees from included transactions.
- **Block Verification:** Nodes independently verify PoW, parent hash, and all included transactions.
- **Dynamic Difficulty:** Difficulty may be adjusted to maintain target block times.

### 5. **Transaction Fees**

- **Minimum Fee:** Every transaction must include at least the minimum fee (prevents spam).
- **Fee Distribution:** All fees in a block go to the miner (credited after block is mined).

---

## How to Run the Demo

### **1. Start the Node**

```bash
python -m tally.node