import os

from src.utils import logger_helper
from src.utils import database_helper
logger = logger_helper.get_logger(__name__)

APP_DATABASE_FILE_NAME = "start_list_database.db"

APP_DATABASE_FILE = os.path.join(os.getcwd(), "src", "data", "app_dbs", APP_DATABASE_FILE_NAME)

OBJECT_TABLE_MAPPING = {
    "team": "pcm_stg_teams",
    "race": "pcm_stg_races",
    "cyclist": "pcm_stg_cyclists",
}


def delete_model_tables(drop_tables):
    conn = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    database_helper.drop_tables(conn, drop_tables)


def check_for_pcm_data(database_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)

    tables_to_check_dict = {
        "pcm_stg_teams": {"minimum_count": 30},
        "pcm_stg_races": {"minimum_count": 50},
        "pcm_stg_cyclists": {"minimum_count": 10000},
    }

    for table_name, validation_config in tables_to_check_dict.items():
        df = database_helper.run_query(database_connection, f"select * from {table_name}")
        if len(df) > validation_config.get("minimum_count", 10):
            logger.info(f"\t ✅ Table '{table_name}' already contains data for PCM database {database_name}")
        else:
            logger.info(f"\t ❌ Table '{table_name}' does not contains data for PCM database {database_name}")
            return False
    logger.info(f"✅ Model already populated with data from this PCM Database!")
    return True


def check_for_pcm_race(database_name, race_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    logger.info(f"Checking for race with name {race_name} and database_name {database_name}")
    df = database_helper.run_query(database_connection, f"select race_id, LOWER(race_name) as race_name from pcm_stg_races") #{OBJECT_TABLE_MAPPING.get('race')}
    df.head()
    df = df.loc[df.race_name.str.contains(race_name), :]
    if len(df) > 0:
        found_races = df["race_name"].tolist()
        logger.info(f"✅ Found race(s) in PCM '{','.join(found_races)}' from provided race name '{race_name}'")
        return True
    logger.info(f"❌ Found no races in PCM from provided race name '{race_name}'. Check spelling!")
    return False


def delete_old_pcm_data(database_name, table_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    delete_sql = f"delete from {table_name} where database_name = '{database_name}'"
    logger.info(f"Deleting existing data: '{delete_sql}'")
    cursor = database_connection.cursor()
    cursor.execute(delete_sql)
    database_connection.commit()


def insert_pcm_object(database_name, object_name, df):
    assert object_name in OBJECT_TABLE_MAPPING.keys()
    table_name = OBJECT_TABLE_MAPPING.get(object_name)
    delete_old_pcm_data(database_name, table_name)
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    logger.info(f"Inserting {len(df)} rows into table '{table_name}'")
    df.to_sql(
        name=table_name,
        con=database_connection,
        if_exists="append",
        index=False
    )
    database_connection.close()


def insert_start_list_files(df):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    df.to_sql(
        name="stg_start_list_files",
        con=database_helper.get_database_connection(APP_DATABASE_FILE_NAME),
        if_exists="append",
        index=False
    )
    logger.info("Added Start List raw data")

    print(database_helper.run_query(database_connection, "select * from stg_start_list_files"))
    database_connection.close()


def insert_start_list_riders(df, race_name, year):
    logger.info(f"Inserting {len(df)} rows into stg_start_list_cyclists")
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    delete_sql = f"delete from stg_start_list_cyclists where year = {year} and race_name = '{race_name}'"
    logger.info(f"Deleting existing data: '{delete_sql}'")
    cursor = database_connection.cursor()
    cursor.execute(delete_sql)
    database_connection.commit()
    df.to_sql(
        name="stg_start_list_cyclists",
        con=database_connection,
        if_exists="append",
        index=False
    )
    database_connection.close()


def does_start_list_exist(race_name, year):
    logger.info(f"Checking for Start Lists...")
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    df = database_helper.run_query(database_connection, f"select * from stg_start_list_cyclists where race_name = '{race_name}' and year = {year}")
    if len(df) > 0:
        df_last_download = database_helper.run_query(database_connection,
                                       f"select downloaded_at from stg_start_list_files where year = {year} and race_name = '{race_name}' order by downloaded_at desc")
        last_downloaded_at = df_last_download['downloaded_at'].iloc[0]
        logger.info(f"✅ Start List for '{year} - {race_name}' is downloaded as of '{last_downloaded_at}'")
        return True
    logger.info(f"❌ Start List for '{year} - {race_name}' has not been downloaded yet")
    return False


def get_start_list_raw_html(data_source, year, race_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE_NAME)
    df = database_helper.run_query(database_connection, f"select blob_content from stg_start_list_files where data_source = '{data_source}' and year = {year} and race_name = '{race_name}' order by downloaded_at desc")
    return df["blob_content"].iloc[0]


def create_model():
    # Open and read the file as a single buffer
    logger.info(f"Creating Model")
    create_model_sql_file_path = os.path.join(os.getcwd(), "src", "model", "create_model.sql")
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


