from __future__ import annotations

import sqlite3
import json
from typing import Optional, List
from dotenv import load_dotenv
import os

load_dotenv(override = True)

DB_PATH = os.getenv("DB_PATH", "accounts.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                username TEXT PRIMARY KEY,
                cash_balance REAL,
                initial_deposit REAL,
                holdings TEXT
            )
        """)
        c.execute("PRAGMA table_info(accounts)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'strategy' not in columns:
            c.execute("ALTER TABLE accounts ADD COLUMN strategy TEXT DEFAULT 'default'")
        
        if 'portfolio_value_time_series' not in columns:
            c.execute("ALTER TABLE accounts ADD COLUMN portfolio_value_time_series TEXT")
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                tx_type TEXT,
                timestamp REAL,
                symbol TEXT,
                quantity INTEGER,
                price_at_transaction REAL,
                amount REAL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS market (
                date TEXT PRIMARY KEY,
                data TEXT
            )
        """)
        conn.commit()
init_db()

def write_account(acc) -> None:
    holdings_json = json.dumps(acc.holdings)
    time_series_json = json.dumps(acc.portfolio_value_time_series)
    with sqlite3.connect(DB_PATH) as conn:
        try:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO accounts
                (username, cash_balance, initial_deposit, holdings, strategy, portfolio_value_time_series)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                acc.username,
                acc.cash_balance,
                acc.initial_deposit,
                holdings_json,
                getattr(acc, "strategy", "default"),
                time_series_json,
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise

def read_account(username: str, price_provider = None) -> Optional["Account"]:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT cash_balance, initial_deposit, holdings, strategy, portfolio_value_time_series
            FROM accounts WHERE username = ?
        """, (username,))
        row = c.fetchone()
    if row is None:
        return None
    cash, initial, holdings_json, strategy, time_series_json = row
    try:
        holdings = json.loads(holdings_json)
    except json.JSONDecodeError:
        holdings = {}
    from accounts import Account, get_share_price
    if price_provider is None:
        price_provider = get_share_price
    acc = Account.__new__(Account)
    acc.username = username
    acc.cash_balance = cash
    acc.initial_deposit = initial
    acc.price_provider = price_provider
    acc.holdings = holdings
    acc.strategy = strategy
    acc.transactions = read_log(username)
    try:
        acc.portfolio_value_time_series = json.loads(time_series_json) if time_series_json else []
    except json.JSONDecodeError:
        acc.portfolio_value_time_series = []
    return acc

def write_log(tx, username: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO logs
            (username, tx_type, timestamp, symbol, quantity, price_at_transaction, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            tx.tx_type.value,
            tx.timestamp,
            tx.symbol,
            tx.quantity,
            tx.price_at_transaction,
            tx.amount,
        ))
        conn.commit()
def read_log(username: str) -> List["Transaction"]:
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT tx_type, timestamp, symbol, quantity, price_at_transaction, amount
            FROM logs WHERE username = ?
            ORDER BY timestamp
        """, (username,))
        rows = c.fetchall()
    from accounts import Transaction, TransactionType
    transactions = []
    for tx_type_str, timestamp, symbol, quantity, price, amount in rows:
        transactions.append(Transaction(
            tx_type = TransactionType(tx_type_str),
            timestamp = timestamp,
            symbol = symbol,
            quantity = quantity,
            price_at_transaction = price,
            amount = amount,
        ))
    return transactions

def write_market(date: str, data: dict) -> None:
    data_json = json.dumps(data)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO market (date, data)
            VALUES (?, ?)
        """, (date, data_json))
        conn.commit()
def read_market(date: str) -> Optional[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT data FROM market WHERE date = ?
        """, (date,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None