import logging
from config import LOG_CONSOLE
from log_handling.sqlite_handler import SQLiteHandler

def init_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # SQLite Handler für DB
    sqlite_handler = SQLiteHandler()
    sqlite_handler.setLevel(logging.DEBUG)
    logger.addHandler(sqlite_handler)

    # Console Handler für Entwicklung (optional)
    if LOG_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
