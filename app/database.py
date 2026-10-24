"""SQLite persistence for the simulated Aftermath payment service."""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("AFTERMATH_DB_PATH", Path(__file__).resolve().parent.parent / "aftermath.db"))

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                amount REAL NOT NULL CHECK (amount > 0),
                currency TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('succeeded', 'failed')),
                description TEXT,
                idempotency_key TEXT UNIQUE,
                failure_reason TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()

def insert_payment(payment):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO payments
            (id, amount, currency, status, description, idempotency_key, failure_reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payment["id"], payment["amount"], payment["currency"], payment["status"],
            payment.get("description"), payment.get("idempotency_key"),
            payment.get("failure_reason"), payment["created_at"]
        ))
        conn.commit()

def find_by_id(payment_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
        return dict(row) if row else None

def find_by_idempotency_key(key):
    if not key:
        return None
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM payments WHERE idempotency_key = ?", (key,)).fetchone()
        return dict(row) if row else None

def list_payments(limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM payments ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
