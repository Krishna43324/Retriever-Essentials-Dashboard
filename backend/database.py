
"""MySQL connection helpers for the Retriever Essentials Dashboard.
 
Configuration is read from environment variables so the same code works
with a local MySQL server and with the MySQL service in Docker Compose.
"""
 
import os
import time
from typing import Any, Optional
 
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
        return bool(cursor.fetchall())  # one row back means the query ran
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
 
 
# ---------------------------------------------------------------------------
# Query helpers
#
# Every helper opens its own short-lived connection and always closes it, so
# callers never have to manage connections or cursors.
# ---------------------------------------------------------------------------
 
DEFAULT_DEPARTMENT = "Retriever Essentials"
 
 
def _run(
    query: str, params: tuple = (), *, fetch: str = "none", commit: bool = False
) -> Any:
    """Run one query. fetch is 'one', 'all', or 'none'. Returns rows or lastrowid."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if fetch == "one":
            result = cursor.fetchone()
        elif fetch == "all":
            result = cursor.fetchall()
        else:
            result = cursor.lastrowid
        if commit:
            connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
 
 
def get_department_id(name: str = DEFAULT_DEPARTMENT) -> Optional[int]:
    row = _run("SELECT dep_id FROM departments WHERE dep_name = %s", (name,), fetch="one")
    return row["dep_id"] if row else None
 
 
def get_user_by_username(username: str) -> Optional[dict]:
    return _run(
        "SELECT user_id, username, password_hash, role, dep_id "
        "FROM users WHERE username = %s",
        (username,),
        fetch="one",
    )
 
 
def create_user(username: str, password_hash: str, role: str = "staff",
                dep_id: Optional[int] = None) -> int:
    """Insert a user and return the new user_id. Raises IntegrityError on duplicates."""
    return _run(
        "INSERT INTO users (username, password_hash, role, dep_id) "
        "VALUES (%s, %s, %s, %s)",
        (username, password_hash, role, dep_id),
        commit=True,
    )
 
 
def ensure_admin_user(username: str, password: str) -> None:
    """Create the bootstrap admin account if no admin exists yet.
 
    Credentials come from ADMIN_USERNAME / ADMIN_PASSWORD. Only the bcrypt
    hash is stored. Does nothing when an admin already exists, so changing the
    env var later will not overwrite or duplicate accounts.
    """
    import bcrypt  # local import keeps this module importable without bcrypt
 
    if not username or not password:
        print("ADMIN_USERNAME / ADMIN_PASSWORD not set; skipping admin bootstrap.")
        return
    existing = _run("SELECT user_id FROM users WHERE role = 'admin' LIMIT 1", fetch="one")
    if existing:
        return
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    create_user(username, hashed, role="admin", dep_id=get_department_id())
    print(f"Created bootstrap admin user '{username}'.")
 
 
def get_csv_by_dataset_name(dataset_name: str) -> Optional[dict]:
    return _run(
        "SELECT csv_id, dataset_name, file_path, uploader_id "
        "FROM csv_files WHERE dataset_name = %s",
        (dataset_name,),
        fetch="one",
    )
 
 
def insert_csv_file(dataset_name: str, file_name: str, file_path: str,
                    file_size_bytes: int, row_count: int, uploader_id: int,
                    dep_id: Optional[int] = None) -> int:
    return _run(
        "INSERT INTO csv_files (dataset_name, file_name, file_path, "
        "file_size_bytes, row_count, uploader_id, dep_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (dataset_name, file_name, file_path, file_size_bytes, row_count,
         uploader_id, dep_id),
        commit=True,
    )
 
 
def delete_csv_file(csv_id: int) -> None:
    _run("DELETE FROM csv_files WHERE csv_id = %s", (csv_id,), commit=True)
 