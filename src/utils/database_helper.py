import sys
import sqlite3
from utils import logger_helper

logger = logger_helper.get_logger(__name__)

def get_database_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        logger.info(f"Connecting to database file: '{db_file}'")
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  # Enable row access by name
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: '{e}'")
        sys.exit(1)
    return conn

def run_query(conn, query, params=()):
    """Execute a query and return the results."""
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error executing query: {e}")
        return None

def list_tables(conn):
    """List all tables in the connected database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    return run_query(conn, query)

def close_connection(conn):
    """Close the database connection."""
    if conn:
        conn.close()

def get_metadata(conn, table_name):
    pragma_sql = f'PRAGMA table_info({table_name})'
    cursor = conn.cursor()
    cursor.execute(pragma_sql)
    columns_info = cursor.fetchall()
    return columns_info

def get_columns(conn, table_name):
    columns_info = get_metadata(conn, table_name)
    columns = [_tuple[1] for _tuple in columns_info]
    return columns