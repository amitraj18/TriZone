import sqlite3
import sys
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import DATABASE_PATH

def resolve_db_path(custom_path=None):
    if custom_path:
        return custom_path
    try:
        from flask import current_app
        if current_app and "DATABASE" in current_app.config:
            return current_app.config["DATABASE"]
    except Exception:
        pass
    import os
    env_db = os.environ.get("DATABASE")
    if env_db:
        return env_db
    return DATABASE_PATH

def get_db_connection(db_path=None):
    """Returns a SQLite connection with Row factory and foreign keys enabled."""
    target_path = resolve_db_path(db_path)
    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db_session(db_path=None):
    """Context manager for transactional database operations."""
    conn = get_db_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
