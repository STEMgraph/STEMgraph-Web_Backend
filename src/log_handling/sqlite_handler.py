import logging
import json
import sqlite3
from datetime import datetime
from log_handling.log_db import LOG_DB_PATH

class SQLiteHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.conn = None

    def _get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(LOG_DB_PATH, check_same_thread=False)
        return self.conn

    def emit(self, record):
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            # Konvertiere timestamp zu ISO-String
            timestamp = datetime.utcfromtimestamp(record.created).isoformat() + "Z"

            details = None
            if isinstance(record.args, dict):
                details = json.dumps(record.args)

            cur.execute("""
                INSERT INTO logs (timestamp, level, component, message, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                timestamp,
                record.levelname,
                record.name,
                record.getMessage(),
                details
            ))

            conn.commit()
        except Exception as e:
            self.handleError(record)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        super().close()
