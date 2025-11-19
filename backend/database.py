import sqlite3
import os

DB_PATH = "data/promotia.db"
SCHEMA_PATH = "data/schema.sql"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    with get_db_connection() as conn:
        with open(SCHEMA_PATH, "r") as f:
            schema = f.read()
        conn.executescript(schema)
        conn.commit()
    print(f"Database initialized at {DB_PATH}")
