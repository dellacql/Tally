# tally/ledger.py
from decimal import Decimal, getcontext
from .transaction import Transaction

getcontext().prec = 42
ACCOUNT_CREATION_FEE = Decimal("0.001")
MIN_NEW_ACCOUNT_AMOUNT = Decimal("0.0000000001")
MIN_TX_FEE = Decimal("0.0001")

class Ledger:
    def __init__(self, initial_balances):
        self.balances = {k: Decimal(str(v)) for k, v in initial_balances.items()}
        self.nonces = {k: 0 for k in self.balances}
        self.total_supply = sum(self.balances.values())
        self.fee_collected = Decimal("0")
        self.stakes = {}  # Add staking information
    
    def stake(self, addr, amount):
        if addr not in self.balances:
            raise ValueError("Address not found")
        if self.balances[addr] < amount:
            raise ValueError("Insufficient funds to stake")
        self.balances[addr] -= amount
        self.stakes[addr] = self.stakes.get(addr, Decimal("0")) + amount

    def unstake(self, addr, amount):
        if addr not in self.stakes:
            raise ValueError("No stake found for address")
        if self.stakes[addr] < amount:
            raise ValueError("Insufficient stake to unstake")
        self.balances[addr] += amount
        self.stakes[addr] -= amount
        if self.stakes[addr] == Decimal("0"):
            del self.stakes[addr]

    def pretty_balances(self):
        for k, v in self.balances.items():
            print(f"Short acct {k[:40]}...: {v}")

    def validate_transaction(self, tx: Transaction):
        try: tx.verify_signature()
        except Exception:
            print("[!] Reject: Invalid signature"); return False
        if tx.sender_addr not in self.balances:
            print("[!] Reject: Sender address not found"); return False
        expected_nonce = self.nonces.get(tx.sender_addr, 0)
        if tx.nonce != expected_nonce:
            print(f"[!] Reject: Bad nonce. Got {tx.nonce}, expected {expected_nonce}"); return False
        total_cost = tx.amount
        if tx.fee < MIN_TX_FEE:
            print("[!] Reject: Fee too low")
            return False
        if tx.new_account_addr:
            total_cost += ACCOUNT_CREATION_FEE
            if tx.amount < MIN_NEW_ACCOUNT_AMOUNT:
                print("[!] Reject: Amount sent for new account too small"); return False
            if tx.new_account_addr in self.balances:
                print("[!] Reject: New account already exists"); return False
        if self.balances[tx.sender_addr] < total_cost:
            print("[!] Reject: Insufficient funds including fees"); return False
        if tx.amount < Decimal("0"):
            print("[!] Reject: Negative send amount"); return False
        return True

    def execute_transaction(self, tx: Transaction):
        if not self.validate_transaction(tx): return False

        total_cost = tx.amount + tx.fee
        if tx.new_account_addr:
            total_cost += ACCOUNT_CREATION_FEE

        self.balances[tx.sender_addr] -= total_cost

        if tx.recipient_addr not in self.balances:
            self.balances[tx.recipient_addr] = Decimal("0")
        self.balances[tx.recipient_addr] += tx.amount

        # Handle creation of new account
        if tx.new_account_addr and tx.new_account_addr not in self.nonces:
            print(f"[*] New account created: {tx.new_account_addr[:42]}..., by funding from {tx.sender_addr[:42]}...")
            self.nonces[tx.new_account_addr] = 0

        if tx.new_account_addr:
            self.fee_collected += ACCOUNT_CREATION_FEE

        self.fee_collected += tx.fee  # Always add transaction fee

        self.nonces[tx.sender_addr] += 1

        current = sum(self.balances.values()) + self.fee_collected
        if abs(current - self.total_supply) > Decimal('1e-30'):
            print(f"Balances sum: {sum(self.balances.values())}")
            print(f"Fee collected: {self.fee_collected}")
            print(f"Total supply: {self.total_supply}")
            print(f"Supply check: {sum(self.balances.values()) + self.fee_collected}")
            raise Exception("Supply invariant broken!")
        return True

    def clone(self):
        new = Ledger({})
        new.balances = self.balances.copy()
        new.nonces = self.nonces.copy()
        new.total_supply = self.total_supply
        new.fee_collected = self.fee_collected
        return new