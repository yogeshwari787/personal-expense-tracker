"""
database.py - SQLite Database Schema & Persistence Layer
Handles creation, indexing, querying, and updating transactions, categories, and budgets.
"""

import sqlite3
import os
from typing import List, Tuple, Dict, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expenses.db")


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Creates and returns a SQLite database connection with row factory enabled."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes tables for transactions, categories, and monthly budgets."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category_type TEXT DEFAULT 'Expense'  -- 'Expense' or 'Income'
    );

    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tx_date TEXT NOT NULL,                -- Format: YYYY-MM-DD
        category_id INTEGER,
        amount REAL NOT NULL,                 -- Positive for expense/spend, or signed convention
        payment_method TEXT NOT NULL,         -- UPI, Credit Card, Debit Card, Cash, Net Banking
        description TEXT,
        account TEXT DEFAULT 'Primary Account',
        raw_source TEXT DEFAULT 'Manual/CSV',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id),
        UNIQUE(tx_date, description, amount, payment_method)
    );

    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,                  -- Format: YYYY-MM
        category_name TEXT NOT NULL,
        limit_amount REAL NOT NULL,
        UNIQUE(month, category_name)
    );

    -- Indexes for high-speed analytical queries
    CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions (tx_date);
    CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions (category_id);
    CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets (month);
    """)

    # Populate default categories if empty
    default_categories = [
        ("Groceries", "Expense"),
        ("Food & Dining", "Expense"),
        ("Rent & Housing", "Expense"),
        ("Utilities", "Expense"),
        ("Transportation", "Expense"),
        ("Entertainment", "Expense"),
        ("Health & Fitness", "Expense"),
        ("Shopping", "Expense"),
        ("Subscriptions", "Expense"),
        ("Miscellaneous", "Expense"),
        ("Income", "Income"),
        ("Investment", "Income")
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO categories (name, category_type) VALUES (?, ?);",
        default_categories
    )
    conn.commit()
    conn.close()


def insert_transaction(
    tx_date: str,
    category_name: str,
    amount: float,
    payment_method: str,
    description: str,
    account: str = "Primary Account",
    db_path: str = DEFAULT_DB_PATH
) -> bool:
    """Inserts a single transaction record, linking or creating the category."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    try:
        cur.execute("INSERT OR IGNORE INTO categories (name) VALUES (?);", (category_name,))
        cur.execute("SELECT id FROM categories WHERE name = ?;", (category_name,))
        cat_row = cur.fetchone()
        category_id = cat_row["id"] if cat_row else None

        cur.execute("""
            INSERT OR IGNORE INTO transactions 
            (tx_date, category_id, amount, payment_method, description, account)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (tx_date, category_id, amount, payment_method, description, account))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def fetch_all_transactions(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Fetches all transactions joined with category names."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            t.id,
            t.tx_date,
            COALESCE(c.name, 'Uncategorized') AS category,
            c.category_type,
            t.amount,
            t.payment_method,
            t.description,
            t.account
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.tx_date DESC, t.id DESC;
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
