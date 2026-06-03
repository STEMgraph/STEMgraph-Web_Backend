import pymysql

from config import (
    MARIADB_HOST,
    MARIADB_PORT,
    MARIADB_USER,
    MARIADB_PASSWORD,
    MARIADB_NAME,
)


def get_connection():
    return pymysql.connect(
        host=MARIADB_HOST,
        port=MARIADB_PORT,
        user=MARIADB_USER,
        password=MARIADB_PASSWORD,
        database=MARIADB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
