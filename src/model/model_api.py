import os

from utils import logger_helper
from utils import database_helper
logger = logger_helper.get_logger(__name__)

APP_DATABASE_FILE_NAME = "start_list_database.db"

APP_DATABASE_FILE = os.path.join("data", "app_dbs", APP_DATABASE_FILE_NAME)


def delete_model_tables():
    conn = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    drop_tables = ["stg_start_list_files"]
    database_helper.drop_all_tables(conn, drop_tables)


def insert_start_list_files(df):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    df.to_sql(
        name="stg_start_list_files",
        con=database_helper.get_database_connection(APP_DATABASE_FILE_NAME),
        if_exists="append",
        index=False
    )
    logger.info("Row Inserted!")

    print(database_helper.run_query(database_connection, "select * from stg_start_list_files"))


def insert_start_list_riders(df):
    logger.info(f"Inserting {len(df)} rows into stg_start_list_cyclists")
    df.to_sql(
        name="stg_start_list_cyclists",
        con=database_helper.get_database_connection(APP_DATABASE_FILE_NAME),
        if_exists="append",
        index=False
    )


def get_start_list_raw_html(data_source, year, race_name):
    results = database_helper.run_query(database_helper.get_database_connection(APP_DATABASE_FILE_NAME), f"select blob_content from stg_start_list_files where data_source = '{data_source}' and year = '{year}' and race_name = '{race_name}' order by downloaded_at desc limit 1")
    return results[0][0]


def create_model():
    # Open and read the file as a single buffer
    logger.info(f"Creating Model")
    create_model_sql_file_path = "model/create_model.sql"
    try:
        with open(create_model_sql_file_path, 'r') as file:
            create_model_sql = file.read()
    except Exception as e:
        logger.error(f"Failed to open file '{create_model_sql_file_path}'")
        logger.exception(e)

    create_tables_sql = create_model_sql.split(';')

    conn = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    # Execute every command from the input file
    for create_table_sql in create_tables_sql:
        logger.debug(f"Executing DDL:\n {create_table_sql}")
        try:
            conn.execute(create_table_sql)
        except Exception as e:
            print(e)


