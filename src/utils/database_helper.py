import sys
import sqlite3
import pandas
from src.utils import logger_helper
from src.utils import database_helper
logger = logger_helper.get_logger(__name__)


def get_database_connection(database_file):
    try:
        conn = sqlite3.connect(
            database_file,
            isolation_level=None,
            detect_types=sqlite3.PARSE_COLNAMES
        )
    except Exception as e:
        print(e)
        sys.exit(1)
    return conn


def list_tables(database_connection):
    conn = database_connection
    sql_query = """SELECT name FROM sqlite_master  
      WHERE type='table';"""
    cursor = conn.cursor()
    cursor.execute(sql_query)
    tables = cursor.fetchall()
    return tables


def get_metadata(database_connection, table_name):
    pragma_sql = f'PRAGMA table_info({table_name})'
    cursor = database_connection.cursor()
    cursor.execute(pragma_sql)
    columns_info = cursor.fetchall()
    return columns_info

def get_columns(database_connection, table_name):
    columns_info = get_metadata(database_connection, table_name)
    columns = [_tuple[1] for _tuple in columns_info]
    return columns


def run_query(database_connection, sql_query):
    conn = database_connection
    df = pandas.read_sql(sql_query, conn)
    return df


def drop_tables(database_connection, tables):
    for drop_table in tables:
        logger.info(f"Dropping table {drop_table}")
        try:
            database_connection.execute(f"drop table if exists {drop_table}")
            database_connection.commit()
        except Exception as e:
            print(e)