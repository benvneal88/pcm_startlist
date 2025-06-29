import sys
import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine
from utils import logger_helper

logger = logger_helper.get_logger(__name__)

def get_database_connection(db_file=None, db_url=None):
    """Get database connection - supports both SQLite and PostgreSQL"""
    if db_url:
        # PostgreSQL connection
        logger.info(f"Connecting to PostgreSQL database")
        engine = create_engine(db_url)
        return engine
    else:
        # SQLite connection (fallback)
        logger.info(f"Connecting to SQLite database: {db_file}")
        return sqlite3.connect(db_file)

def run_query(connection, query):
    """Execute query and return results as DataFrame"""
    if hasattr(connection, 'execute'):
        # SQLite connection
        return pd.read_sql_query(query, connection)
    else:
        # SQLAlchemy engine (PostgreSQL)
        return pd.read_sql_query(query, connection)

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