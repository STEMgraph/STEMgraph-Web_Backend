import sqlite3
import os
from datetime import datetime, timedelta
from config import LOG_DB_PATH, MAX_LOG_SIZE_MB, MAX_LOG_AGE_DAYS


def get_connection():
    os.makedirs(os.path.dirname(LOG_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(LOG_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_log_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            component TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()


def rotate_logs():
    # 1. Größe prüfen
    if os.path.exists(LOG_DB_PATH):
        size_mb = os.path.getsize(LOG_DB_PATH) / (1024 * 1024)
        if size_mb > MAX_LOG_SIZE_MB:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM logs WHERE id IN (SELECT id FROM logs ORDER BY id LIMIT 1000)")
            conn.commit()
            conn.close()

    # 2. Alter prüfen
    cutoff = datetime.utcnow() - timedelta(days=MAX_LOG_AGE_DAYS)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM logs WHERE timestamp < ?", (cutoff.isoformat() + "Z",))
    conn.commit()
    conn.close()
