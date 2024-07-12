import pandas as pd

from model import model_api
from utils import logger_helper
logger = logger_helper.get_logger(__name__)


DATABASE_FILE = "pcm_dbs/worlddb_2023.sqlite"

OBJECT_TABLE_MAPPING = {
    "team": "DYN_team",
    "race": "STA_race",
    "cyclist": "DYN_cyclist",
}


def get_object(database_connection, object_name):
    assert object_name in OBJECT_TABLE_MAPPING.keys()
    table_name = OBJECT_TABLE_MAPPING.get(object_name)
    if object_name == "team":
        columns = "IDteam as team_id, gene_sz_shortname as team_shortname, gene_sz_name as team_name"
    elif object_name == "race":
        columns = "IDcyclist as cyclist_id, gene_sz_lastname as cyclist_last_name, gene_sz_firstname as cyclist_first_name, gene_sz_firstlastname as cyclist_name, fkIDteam as team_id"
    elif object_name == "cyclist":
        columns = "IDrace as race_id, gene_sz_race_name as race_name, gene_sz_abbreviation as race_abbrreviation, gene_sz_filename as race_filename"
    df = pd.read_sql_query(f"SELECT {columns} FROM {table_name}", database_connection)
    return df


def get_cyclists_teams(database_connection):
    teams_df = get_object(database_connection, "team")
    cyclists_df = get_object(database_connection, "cyclist")
    cyclists_team_df = teams_df.merge(cyclists_df, how="inner", left_on="team_id", right_on="team_id")
    return cyclists_team_df


def get_race_start_list_file_name(database_connection, race_id: int):
    races_df = get_object(database_connection, "race")
    df = races_df[races_df['race_id'] == race_id]
    start_list_file_name = f"{df.race_filename}.xml"
    logger.info(f"start_list file name: '{start_list_file_name}'")
    return start_list_file_name


def list_races(database_connection, name_like=None):
    races_df = get_object(database_connection, "race")

    if name_like:
        df = races_df.loc[races_df.race_name.str.contains(name_like), :]
    else:
        df = races_df

    logger.info(f"List of races:\n {df.head(100)}")
    #logger.info(df.dtypes)
    return df



#if __name__ == "__main__":
    #table_list = list_tables()
    # for table in table_list:
    #     if "team" in table[0]:
    #         print(table)

    #
    # races_df = get_table(RACE_TABLE_NAME)
    # teams_df = get_table(TEAM_TABLE_NAME)
    # cyclists_df = get_table(CYCLIST_TABLE_NAME)

    #get_cyclists_teams()
    #print(get_race_start_list_file_name(race_name_like="Tour de France"))
    #print(get_race_start_list_file_name(race_id=9))

