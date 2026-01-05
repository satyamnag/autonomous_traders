from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

from database import write_account, write_log
from market import get_share_price

# Exceptions
class WalletError(Exception):
    """Base class for wallet/account related errors."""
    pass

class InsufficientFundsError(WalletError):
    """Raised when an operation would leave the cash balance negative."""
    pass

class InsufficientHoldingsError(WalletError):
    """Raised when attempting to sell more shares than held."""
    pass

class InvalidTransactionError(WalletError):
    """Raised for invalid (non-positive) transaction requests."""
    pass

class UnknownSymbolError(WalletError):
    """Raised when a price lookup cannot resolve the symbol."""
    pass

# Transaction type
class TransactionType(Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    BUY = "buy"
    SELL = "sell"

PriceProvider = Callable[[str], float]

# Transaction record
@dataclass
class Transaction:
    tx_type: TransactionType
    timestamp: float
    symbol: Optional[str]
    quantity: Optional[int]
    price_at_transaction: float
    amount: float

class Account:
    """A simple trading account tracking cash, holdings, and a chronological transaction history."""
    def __init__(
        self,
        username: str,
        initial_deposit: float,
        price_provider: PriceProvider = get_share_price
    ) -> None:
        if initial_deposit < 0:
            raise InvalidTransactionError("Initial deposit must be non-negative")
        self.username: str = username
        self.cash_balance: float = initial_deposit
        self.initial_deposit: float = initial_deposit        
        self.price_provider: PriceProvider = price_provider
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Transaction] = []
        tx = self._record_transaction(
            TransactionType.DEPOSIT,
            initial_deposit,
            symbol = None,
            quantity = None,
            price_at_transaction = 0.0
        )
        self.strategy: str = "default"
        self.portfolio_value_time_series: List[Tuple[str, float]] = []
        write_account(self)
    
    def _lookup_price(self, symbol: str) -> float:
        try:
            return self.price_provider(symbol)
        except Exception as e:
            raise UnknownSymbolError(f"Price lookup failed: {e}") from e

    def _record_transaction(
        self,
        tx_type: TransactionType,
        amount: float,
        symbol: Optional[str],
        quantity: Optional[int],
        price_at_transaction: float
    ) -> Transaction:
        tx = Transaction(
            tx_type = tx_type,
            timestamp = time.time(),
            symbol = symbol,
            quantity = quantity,
            price_at_transaction = price_at_transaction,
            amount = amount,
        )
        self.transactions.append(tx)
        return tx
    
    def deposit(self, amount: float) -> None:
        """Deposit funds into the account to increase cash balance."""
        if amount <= 0:
            raise InvalidTransactionError("Deposit amount must be positive")
        self.cash_balance += amount
        tx = self._record_transaction(
            TransactionType.DEPOSIT,
            amount,
            symbol = None,
            quantity = None,
            price_at_transaction = 0.0
        )
        write_log(tx, self.username)
        write_account(self)
    
    def withdraw(self, amount: float) -> None:
        """Withdraw funds from the account if sufficient balance exists."""
        if amount <= 0:
            raise InvalidTransactionError("Withdrawal amount must be positive")
        if self.cash_balance - amount < 0:
            raise InsufficientFundsError("Insufficient funds for withdrawal")
        self.cash_balance -= amount
        tx = self._record_transaction(
            TransactionType.WITHDRAWAL,
            -amount,
            symbol = None,
            quantity = None,
            price_at_transaction = 0.0
        )        
        write_log(tx, self.username)
        write_account(self)
    
    def buy(self, symbol: str, quantity: int) -> None:
        """Purchase a quantity of shares of the given symbol using available cash."""
        if quantity <= 0:
            raise InvalidTransactionError("Buy quantity must be positive")
        price = self._lookup_price(symbol)
        total_cost = quantity * price
        if total_cost > self.cash_balance:
            raise InsufficientFundsError("Insufficient funds to buy")
        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        tx = self._record_transaction(
            TransactionType.BUY,
            -total_cost,
            symbol = symbol,
            quantity = quantity,
            price_at_transaction = price
        )
        write_log(tx, self.username)
        write_account(self)
    
    def sell(self, symbol: str, quantity: int) -> None:
        """Sell a quantity of shares of the given symbol, increasing cash balance."""
        if quantity <= 0:
            raise InvalidTransactionError("Sell quantity must be positive")
        current = self.holdings.get(symbol, 0)
        if current < quantity:
            raise InsufficientHoldingsError("Not enough holdings to sell")
        price = self._lookup_price(symbol)
        proceeds = quantity * price
        self.cash_balance += proceeds
        new_qty = current - quantity
        if new_qty > 0:
            self.holdings[symbol] = new_qty
        else:
            self.holdings.pop(symbol, None)
        tx = self._record_transaction(
            TransactionType.SELL,
            proceeds,
            symbol = symbol,
            quantity = quantity,
            price_at_transaction = price
        )
        write_log(tx, self.username)
        write_account(self)
    
    def get_portfolio_value(self) -> float:
        """Compute current total portfolio value: cash balance plus market value of holdings."""
        value = float(self.cash_balance)
        for symbol, qty in self.holdings.items():
            price = self._lookup_price(symbol)
            value += qty * price
        return value
    
    def get_profit_loss(self) -> float:
        """Profit or loss relative to the initial deposit, based on current portfolio value."""
        return self.get_portfolio_value() - self.initial_deposit
    
    def get_holdings(self) -> List[Tuple[str, int]]:
        """Return a sorted list of (symbol, quantity) for holdings with positive quantity."""
        return sorted((symbol, qty) for symbol, qty in self.holdings.items() if qty > 0)
    
    def list_transactions(self) -> List[Transaction]:
        """Return a shallow copy of the chronological transaction history."""
        return list(self.transactions)
    
    def serialize_transaction(self, tx: Transaction) -> dict:
        """Serialize a transaction to a JSON-friendly dict."""
        return {
            "type": tx.tx_type.value,
            "timestamp": tx.timestamp,
            "symbol": tx.symbol,
            "quantity": tx.quantity,
            "price_at_transaction": tx.price_at_transaction,
            "amount": tx.amount,
        }
    
    def report(self) -> str:
        """Return a JSON string representing the account."""
        portfolio_value = self.get_portfolio_value()
        self.portfolio_value_time_series.append(
            (
                datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                portfolio_value
            )
        )
        pnl = self.get_profit_loss()
        data = {
            "username": self.username,
            "cash_balance": self.cash_balance,
            "initial_deposit": self.initial_deposit,
            "strategy": self.strategy,
            "holdings": self.holdings,
            "transactions": [self.serialize_transaction(tx) for tx in self.transactions],
            "portfolio_value_time_series": self.portfolio_value_time_series
        }
        data["total_portfolio_value"] = portfolio_value
        data["total_profit_loss"] = pnl
        write_account(self)
        return json.dumps(data)
    
    def get_strategy(self) -> str:
        """Return the strategy of the account."""
        return self.strategy
    
    def change_strategy(self, strategy: str) -> None:
        """At your discretion, if you choose to, call this to change your investment strategy for the future."""
        if not strategy:
            raise ValueError("Strategy must be a non-empty string")
        self.strategy = strategy
        write_account(self)