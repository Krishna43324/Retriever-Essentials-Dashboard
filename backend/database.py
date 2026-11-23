"""MySQL connection helpers for the Retriever Essentials Dashboard.

Configuration is read from environment variables so the same code works
with a local MySQL server and with the MySQL service in Docker Compose.
"""

import os
import time
from typing import Optional

import mysql.connector
from mysql.connector import Error


def _database_config() -> dict:
    """Build a fresh connector configuration from the current environment."""
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "retriever_dashboard"),
        "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", "10")),
        "charset": "utf8mb4",
        "collation": "utf8mb4_0900_ai_ci",
    }


def get_db_connection():
    """Open and return a MySQL connection. The caller must close it."""
    return mysql.connector.connect(**_database_config())


def check_database_connection() -> bool:
    """Return True when MySQL can execute a simple query."""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        return cursor.fetchone()[0] == 1
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def wait_for_database(
    attempts: Optional[int] = None, delay_seconds: Optional[float] = None
) -> None:
    """Retry the connection during startup while the DB service becomes ready."""
    attempts = attempts or int(os.getenv("DB_STARTUP_ATTEMPTS", "20"))
    delay_seconds = (
        delay_seconds
        if delay_seconds is not None
        else float(os.getenv("DB_STARTUP_DELAY", "2"))
    )

    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            if check_database_connection():
                print("Connected to MySQL database successfully.")
                return
        except Error as error:
            last_error = error
            print(f"Waiting for MySQL ({attempt}/{attempts}): {error}")
        if attempt < attempts:
            time.sleep(delay_seconds)

    raise RuntimeError(
        f"Could not connect to MySQL after {attempts} attempts. "
        "Check DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, and DB_NAME."
    ) from last_error
