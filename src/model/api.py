import sqlite3


def get_database_conn(database_file):
    try:
        conn = sqlite3.connect(
            database_file,
            isolation_level=None,
            detect_types=sqlite3.PARSE_COLNAMES)
    except Exception as e:
        print(e)
        return None
    return conn


def list_tables(database_connection):
    sql_query = """SELECT name FROM sqlite_master  
      WHERE type='table';"""
    cursor = database_connection.cursor()
    cursor.execute(sql_query)
    tables = cursor.fetchall()
    return tables

def drop_all_tables(database_connection):
    pass