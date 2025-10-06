"""Módulo simples para interação com o banco de catálogo (SQLite)."""
from typing import List, Optional, Dict, Any
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "catalog.db"


def get_connection(read_only: bool = False) -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if read_only:
        uri = f"file:{DB_PATH}?mode=ro"
        return sqlite3.connect(uri, uri=True)
    return sqlite3.connect(str(DB_PATH))


def execute_sql_file(conn: sqlite3.Connection, sql_file: str) -> None:
    with open(sql_file, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn:
        conn.executescript(sql)


def add_category(name: str) -> int:
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES(?)", (name,))
        conn.commit()
        cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
        row = cur.fetchone()
        return row[0]


def add_product(name: str, price_cents: int, sku: Optional[str] = None, stock: int = 0,
                description: Optional[str] = None, category_id: Optional[int] = None,
                image_url: Optional[str] = None) -> int:
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO products(name, description, price_cents, sku, stock, category_id, image_url)
            VALUES(?,?,?,?,?,?,?)
            """,
            (name, description, price_cents, sku, stock, category_id, image_url),
        )
        conn.commit()
        return cur.lastrowid


def list_products(limit: int = 100) -> List[Dict[str, Any]]:
    with closing(get_connection(read_only=True)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT p.*, c.name as category FROM products p LEFT JOIN categories c ON p.category_id = c.id ORDER BY p.id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]


def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    with closing(get_connection(read_only=True)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT p.*, c.name as category FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.id = ?", (product_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def update_product(product_id: int, **kwargs) -> bool:
    """Update allowed product fields. Returns True if a row was updated."""
    allowed = {"name", "description", "price_cents", "sku", "stock", "category_id", "image_url"}
    keys = [k for k in kwargs.keys() if k in allowed]
    if not keys:
        return False
    with closing(get_connection()) as conn:
        cur = conn.cursor()
        set_clause = ", ".join(f"{k} = ?" for k in keys)
        values = [kwargs[k] for k in keys]
        values.append(product_id)
        cur.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return cur.rowcount > 0
