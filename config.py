import sqlite3


# ----------------- Database Setup -----------------

def db_connect():
    conn = sqlite3.connect("grocery.db", check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT,
        product_name TEXT,
        expiry_date TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    return conn
