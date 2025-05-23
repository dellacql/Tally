Tally: A Proof-of-Stake pBFT Blockchain

##Introduction
   Tally is a cryptocurrency and distributed ledger system designed around a unique combination of fixed-supply digital coin and practical Byzantine Fault Tolerance (pBFT) consensus with Proof-of-Stake (PoS) validator        selection. Tally aims to provide a fast, secure, energy-efficient blockchain with minimal resource requirements and robust protection against fraud and Sybil attacks. This document gives an overview of Tally’s high-       level design, with special emphasis on its coin’s mathematical and cryptographic properties.

Coin Model and Properties
1. Fixed-Supply, Infinitely-Divisible Token
Genesis Allocation:
Upon chain creation, 100% of Tally’s coin is initialized in a single genesis account. The system’s total value, typically represented as 1.0, is set in this first state and can never be increased or reduced. All value in the system exists from the very start; there is neither mining nor inflation, and the system is mathematically protected from deflation by design.
No Minting, No Burning:
Tally prohibits the creation or destruction of tokens after genesis. Coin is never “minted,” “burned,” or otherwise modified in supply. All transactions and state changes are simply redistributions or subdivisions of the original single coin.
Infinite Divisibility:
Tally treats its coin as a high-precision decimal value (e.g., supporting 40 decimal places). This permits coin to be subdivided into arbitrary, practically infinite fragments (i.e., no effective limit to the number of users/transactions that can be supported).
For example, after several transactions, the system might have accounts holding 0.298523..., 0.00000000003123..., etc., but summing all accounts will always equal exactly 1.0.
Account Creation by Division:
New accounts are created only by subdividing existing balances.
There is no way to create a new account with zero value – every new account must be “sponsored” by an existing one that transfers a positive amount. This ensures every account represents a portion of the original genesis supply.
Mathematical Integrity:
The core invariant is always enforced:
Sum of all account balances = 1.0 (the original coin supply).
Every block, every transaction, every update checks this property. No valid transaction or block can ever break it.



2. Transactions, Security, and Sybil Resistance
Cryptographic Security:
All transfers are signed with elliptic curve cryptography and nonces to prevent replay attacks. Transaction validity is checked rigorously before any state update.
Trusted Account Origination:
Accounts can only be created through a signed transaction from an existing account—a built-in safeguard against automated Sybil attacks.
Decentralized Yet Farming-Resistant:
Validator selection and voting power is proportional to actual stake in the supply. Since no one can inflate their balance through artificial means, control always remains proportional to actual at-risk value.
No Extrinsic Inflation Incentive:
Since you cannot “mine” or “mint” new coins, the network is free from inflationary economic design and can remain maximally energy-efficient: no wasted PoW, no race-to-mine arms race, no new issuance.

3. High Throughput and Fluidity
No Hardcoded Block/Transaction Limits:
The protocol sets no software limit on transaction count per block or block production frequency; throughput is entirely bounded by the processing and bandwidth capabilities of the current validator set.
Liquidity and Scalability:
Thanks to infinite divisibility, the system never “runs out” of tokens in practical terms—even trillions of accounts/transactions can be absorbed across arbitrarily many users.

4. Additional Features
Fair, Transparent Genesis:
Every coin is visible on-chain at all times. All accounts and subdivisions are public, auditable, and cryptographically guaranteed.
Lossless, Auditable Bookkeeping:
At any time, all holders, accounts, and balances can be tabulated to verify the full ledger, ensuring maximal network transparency and assurance to users.

## Key Features
Practical Byzantine Fault Tolerance (pBFT): Tally uses a consensus algorithm resilient to up to a third of nodes being malicious, providing strong safety and liveness.
Proof-of-Stake Validator Selection: Only nodes with a minimum stake are eligible to propose and validate blocks; validator power is proportional to staked amount. Leader rotation depends on the current “view” and token holding.
Simplified, Transparent Design: No hidden monetary policy. The entire economics are visible in the present state of the ledger.
Account Creation as a Transaction: New accounts may only be created via transactions funded by existing coin holders. No unbacked “free” accounts.

Practical Byzantine Fault Tolerance (pBFT): A consensus algorithm that allows the network to tolerate up to a third of malicious or faulty nodes, ensuring data integrity and security.
Transactions: Supports standard cryptocurrency transactions including sending and receiving Tally. New account creation is also supported via transactions. By creating a mechanism where only an existing account holder can create a new account through a transaction we can ensure that only trusted parties are able to transact.
Simplified Implementation: This is a simplified simulation that focuses on core PoS pBFT concepts.
Networking: Nodes communicate with each other over TCP sockets. Obviously once we achieve full production mechanism we will ensure a more robust method of communication between verifiers.

## Architecture

Tally consists of the following components:

Node: Participates in consensus, manages a local ledger copy.
Data Object: Holds the state (all balances).
Transaction: Signed coin transfer and/or account-creation request.
Block: Batch of transactions and metadata.
Consensus (PoS pBFT): Validates blocks, rotates leader by view/stake, and ensures honest acceptance and ordering of blocks.


## How it Works

Staking: Users must have a minimum coin balance to become a validator.
Primary Node Selection: Validators are selected deterministically by view/stake.
Block Proposals and Voting: Transaction batches are proposed, voted on, and finalized using pBFT with PoS validator voting.
Supply Integrity: After each block, the sum of all balances is checked and must equal the original genesis total; if not, the block is invalid.
New Account Policy: Only accounts holding a true slice of the genesis supply may sponsor a new account, and every new account must be directly funded with a positive amount.

Example: Lifecycle of a Tally Coin
   Genesis:
   Alice holds 1.0 Tally.
   Alice splits:
   She sends 0.3 to Bob → Alice: 0.7, Bob: 0.3 (Sum: 1.0)
   Bob opens 3 sub-accounts for his children:
   Sends 0.09 each → Bob: 0.03, Child1: 0.09, Child2: 0.09, Child3: 0.09
   Across millions of accounts, the sum of all balances will always be 1.0.

## Running the Simulation

1.  **Prerequisites:**
    *   Python 3.6 or higher.
    *   Cryptography library: `pip install cryptography`

2.  **Configuration:**
    *   `NODE_ADDRESSES`: Configure the IP addresses and ports for each node in the `NODE_ADDRESSES` list.  Ensure that the ports are open on your system.  The current configuration uses localhost addresses (127.0.0.1) on different ports.
    *   `initial_balances`: Modify the initial balances for each node in the `initial_balances` dictionary.
    *   `validator_addresses`: Change which keys you want to use as validators.

3.  **Execution:**
    *   Run the `Tally.py` script.  This will start the simulation, creating three nodes that participate in the blockchain network.

## Notes and Limitations

*   **Simplified Implementation:** This is a simplified simulation for educational and demonstrative purposes.  It lacks features found in real-world blockchains (e.g., networking discovery, persistence, advanced transaction types).
*   **Local Simulation:** The current implementation runs all nodes on a single machine (localhost).  A production blockchain would require nodes to be distributed across multiple machines.
*   **Security Considerations:**  The cryptography used in this simulation is for demonstration purposes only.  A real-world blockchain would require more robust security measures.
*   **No Persistence:** The blockchain data is lost when the simulation is stopped.

  ##Summary Table of Coin Properties
Property	Tally	Bitcoin/Ethereum
Total Supply	Set at genesis, never changes	Increases by mining/block rewards
Divisibility	Up to 40 decimals (or more)	8 (BTC), 18 (ETH)
Can be minted	No	Yes
Can be burned	No (except optional fees)	Yes (ETH: with some tx fees)
Account creation	Only by existing holders, funded	Anyone, typically no min balance


## License
