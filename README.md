# Tally Blockchain

**Tally** is a highly-divisible, fixed-supply, fee-only decentralized blockchain and cryptocurrency system. Tally is designed for speed, liquidity, and security, using robust Proof-of-Work (PoW) for Sybil resistance, with every coin created at genesis and strong mathematical integrity. The system supports modular extension to Proof-of-Stake (PoS) with pBFT consensus.

---

## Table of Contents

- [Features](#features)
- [Coin Model and Properties](#coin-model-and-properties)
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

## How to Run the Demo

### 1. Start the Node

```bash
python -m tally.node
