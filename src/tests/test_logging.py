import os
import sys
import sqlite3
import logging
import tempfile
import pytest
from unittest.mock import patch

# System-Pfad anpassen für Importe
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_handling.logger import init_logger
from log_handling.log_db import init_log_db, rotate_logs
from log_handling.sqlite_handler import SQLiteHandler


# ---------------------------------------------------------
# FIXTURE: Temporäre Log-Datenbank für alle Tests
# ---------------------------------------------------------
@pytest.fixture(scope="function")
def temp_log_db():
    """Erstelle temporäre Log-DB für Tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "log.db")

        # Patches für Config-Variablen
        with patch('log_handling.log_db.LOG_DB_PATH', db_path):
            with patch('log_handling.sqlite_handler.LOG_DB_PATH', db_path):
                # Logging-System initialisieren
                init_log_db()
                
                # Logger clearen und neu initialisieren
                logging.getLogger().handlers.clear()
                init_logger()

                yield db_path


# ---------------------------------------------------------
# HILFSFUNKTION: Log-Einträge aus DB lesen
# ---------------------------------------------------------
def read_logs(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute("SELECT level, component, message, details FROM logs").fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------
# TEST 1: Logging-Handler schreibt Einträge in SQLite
# ---------------------------------------------------------
def test_sqlite_handler_writes_logs(temp_log_db):
    """Teste ob SQLiteHandler Logs korrekt in DB speichert"""
    logger = logging.getLogger("test")
    logger.info("Test message", {"foo": "bar"})

    logs = read_logs(temp_log_db)
    assert len(logs) >= 1
    
    # Finde unseren Test-Log (letzter Eintrag)
    level, component, message, details = logs[-1]
    assert level == "INFO"
    assert component == "test"
    assert "Test message" in message
    assert '"foo": "bar"' in (details or "")


# ---------------------------------------------------------
# TEST 2: Logger schreibt auf verschiedene Level
# ---------------------------------------------------------
def test_logging_levels(temp_log_db):
    """Teste verschiedene Log-Level"""
    logger = logging.getLogger("levels_test")
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    logs = read_logs(temp_log_db)
    
    # Mindestens 5 Logs sollten vorhanden sein
    test_logs = [row for row in logs if row[1] == "levels_test"]
    assert len(test_logs) >= 5
    
    levels = [row[0] for row in test_logs]
    assert "DEBUG" in levels
    assert "INFO" in levels
    assert "WARNING" in levels
    assert "ERROR" in levels
    assert "CRITICAL" in levels


# ---------------------------------------------------------
# TEST 3: JSON-Details werden korrekt gespeichert
# ---------------------------------------------------------
def test_logging_with_details(temp_log_db):
    """Teste ob strukturierte Log-Details korrekt gespeichert werden"""
    logger = logging.getLogger("details_test")
    
    logger.info("User action", {
        "user_id": 123,
        "action": "login",
        "ip": "192.168.1.1"
    })

    logs = read_logs(temp_log_db)
    details_logs = [row for row in logs if row[1] == "details_test"]
    
    assert len(details_logs) >= 1
    details = details_logs[-1][3]
    assert "user_id" in details
    assert "123" in details


# ---------------------------------------------------------
# TEST 4: Log-Rotation löscht alte Einträge
# ---------------------------------------------------------
def test_log_rotation(temp_log_db):
    """Teste ob Log-Rotation alte Einträge löscht"""
    # Viele Logs erzeugen (2000 Einträge)
    logger = logging.getLogger("rotation")
    for i in range(2000):
        logger.info(f"Entry {i}")

    logs_before = read_logs(temp_log_db)
    initial_count = len(logs_before)
    assert initial_count >= 2000, f"Sollten 2000 Logs haben, haben aber {initial_count}"

    # Rotation mit sehr niedrigem Limit erzwingen (0 MB = sofort rotieren)
    with patch('log_handling.log_db.MAX_LOG_SIZE_MB', 0.0001):  # ~100 Bytes
        rotate_logs()

    logs_after = read_logs(temp_log_db)
    final_count = len(logs_after)

    # Rotation sollte alte Einträge gelöscht haben
    assert final_count < initial_count, "Rotation sollte Logs löschen"
    assert final_count > 0, "Nicht alle Logs sollten gelöscht werden"
    print(f"Rotation: {initial_count} → {final_count} Logs")

