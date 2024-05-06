import os
import sqlite3

from utils import logger
logger = logger.get_logger_init()

APP_DATABASE_FILE_NAME = "pcm_startlist_model.db"

APP_DATABASE_FILE = os.path.join("data", "app_dbs", APP_DATABASE_FILE_NAME)


def get_database_conn(database_file=APP_DATABASE_FILE):
    try:
        conn = sqlite3.connect(
            database_file,
            isolation_level=None,
            detect_types=sqlite3.PARSE_COLNAMES)
    except Exception as e:
        print(e)
        return None
    return conn


def list_tables():
    conn = get_database_conn()
    sql_query = """SELECT name FROM sqlite_master  
      WHERE type='table';"""
    cursor = conn.cursor()
    cursor.execute(sql_query)
    tables = cursor.fetchall()
    return tables


def run_query(sql_query):
    conn = get_database_conn()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    results = cursor.fetchall()
    return results


def drop_all_tables(database_connection):
    pass


def insert_start_list_files(df):
    df.to_sql(
        name="stg_start_list_files",
        con=get_database_conn(),
        if_exists="append",
        index=False
    )
    logger.info("Row Inserted!")
    print(run_query("select * from stg_start_list_files"))


def insert_start_list_cyclists(df):
    logger.info(f"Inserting {len(df)} rows into stg_start_list_cyclists")
    df.to_sql(
        name="stg_start_list_cyclists",
        con=get_database_conn(),
        if_exists="append",
        index=False
    )


def fetch_start_list(data_source, year, race_name):
    results = run_query(f"select blob_content from stg_start_list_files where data_source = '{data_source}' and year = '{year}' and race_name = '{race_name}' limit 1")

    return results[0][0]


def create_model():
    # Open and read the file as a single buffer

    logger.info(f"Creating Model")
    with open("model/create_model.sql", 'r') as file:
        create_model_sql = file.read()

    create_tables_sql = create_model_sql.split(';')

    conn = get_database_conn()
    # Execute every command from the input file
    for create_table_sql in create_tables_sql:
        logger.debug(f"Executing DDL:\n {create_table_sql}")
        try:
            conn.execute(create_table_sql)
        except Exception as e:
            print(e)

