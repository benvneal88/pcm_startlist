import os
import sqlite3
import pandas as pd
import utils

logger = utils.get_logger_init()
import scraper

DATA_DIRECTORY = os.path.join("data")

# SQLiteExporter.exe -export  "Pro Cycling Manager 2023\Cloud\Neal\Career_1.cdb"

DATABASE_FILE = "data/worlddb_2023.sqlite"
CYCLIST_TABLE_NAME = "DYN_cyclist"
RACE_TABLE_NAME = "STA_race"
TEAM_TABLE_NAME = "DYN_team"

def get_database_conn(database_file=DATABASE_FILE):
    conn = sqlite3.connect(
        database_file,
        isolation_level=None,
        detect_types=sqlite3.PARSE_COLNAMES)
    return conn


def list_tables():
    database_connection = get_database_conn()
    sql_query = """SELECT name FROM sqlite_master  
      WHERE type='table';"""
    cursor = database_connection.cursor()
    cursor.execute(sql_query)
    tables = cursor.fetchall()
    return tables


def get_table(table_name):
    database_connection = get_database_conn()
    if table_name == TEAM_TABLE_NAME:
        columns = "IDteam as team_id, gene_sz_shortname as team_shortname, gene_sz_name as team_name"
    elif table_name == CYCLIST_TABLE_NAME:
        columns = "IDcyclist as cyclist_id, gene_sz_lastname as last_name, gene_sz_firstname as first_name, gene_sz_firstlastname as name, fkIDteam as team_id"
    elif table_name == RACE_TABLE_NAME:
        columns = "IDrace as race_id, gene_sz_race_name as race_name, gene_sz_abbreviation as race_abbrreviation, gene_sz_filename as race_filename"

    df = pd.read_sql_query(f"SELECT {columns} FROM {table_name}", database_connection)
    return df


def get_cyclists_teams():
    teams_df = get_table(TEAM_TABLE_NAME)
    cyclists_df = get_table(CYCLIST_TABLE_NAME)
    cyclists_team_df = teams_df.merge(cyclists_df, how="inner", left_on="team_id", right_on="team_id")
    return cyclists_team_df


def get_race_startlist_file_name(race_id: int):
    races_df = get_table(RACE_TABLE_NAME)
    df = races_df[races_df['race_id'] == race_id]
    startlist_file_name = f"{df.race_filename}.xml"
    logger.info(f"Startlist file name: '{startlist_file_name}'")
    return startlist_file_name


def list_races(name_like=None):
    races_df = get_table(RACE_TABLE_NAME)

    if name_like:
        df = races_df.loc[races_df.race_name.str.contains(name_like), :]
    else:
        df = races_df

    logger.info(f"List of races:\n {df.head(100)}")
    #logger.info(df.dtypes)
    return df



if __name__ == "__main__":
    #table_list = list_tables()
    # for table in table_list:
    #     if "team" in table[0]:
    #         print(table)

    #
    # races_df = get_table(RACE_TABLE_NAME)
    # teams_df = get_table(TEAM_TABLE_NAME)
    # cyclists_df = get_table(CYCLIST_TABLE_NAME)

    #get_cyclists_teams()
    print(get_race_startlist_file_name(race_name_like="Tour de France"))
    #print(get_race_startlist_file_name(race_id=9))

