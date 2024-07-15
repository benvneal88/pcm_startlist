import os
import pandas
from src.model import model_api
from src.utils import database_helper
from src.utils import logger_helper
logger = logger_helper.get_logger(__name__)


OBJECT_TABLE_MAPPING = {
    "team": "DYN_team",
    "race": "STA_race",
    "cyclist": "DYN_cyclist",
}

PCM_DATABASE_FIELD_MAPPINGS = {
    "2024":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "filename"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        }
}

# def get_race_start_list_file_name(database_connection, race_id: int):
#     races_df = get_object(database_connection, "race")
#     df = races_df[races_df['race_id'] == race_id]
#     start_list_file_name = f"{df.filename}.xml"
#     logger.info(f"start_list file name: '{start_list_file_name}'")
#     return start_list_file_name


def get_object(database_name, object_name, pcm_version="2024"):
    database_connection = database_helper.get_database_connection(get_database_file(database_name))
    assert object_name in OBJECT_TABLE_MAPPING.keys()
    assert pcm_version in PCM_DATABASE_FIELD_MAPPINGS.keys()

    table_name = OBJECT_TABLE_MAPPING.get(object_name)
    database_field_mappings = PCM_DATABASE_FIELD_MAPPINGS.get(pcm_version)

    assert table_name in database_field_mappings.keys()

    table_field_mappings = database_field_mappings.get(table_name)

    table_columns = database_helper.get_columns(database_connection, table_name)
    for column_name in table_field_mappings.keys():
        if column_name not in table_columns:
            logger.error(f"Column {column_name} not found in table")

    columns_select_statements = []
    for column_name, rename_to in table_field_mappings.items():
        columns_select_statements.append(f"{column_name} as {rename_to}")

    select_statement = ",".join(columns_select_statements)

    sql_statement = f"SELECT '{database_name}' as database_name, {select_statement} FROM {table_name}"
    logger.info(f"SQL Statement: '{sql_statement}'")
    df = pandas.read_sql_query(sql_statement, database_connection)
    return df


def get_roster(database_name):
    teams_df = get_object(database_name, "team")
    cyclists_df = get_object(database_name, "cyclist")
    cyclists_team_df = teams_df.merge(cyclists_df, how="inner", left_on="team_id", right_on="team_id")
    return cyclists_team_df


def list_races(database_name, name_like=None):
    races_df = get_object(database_name, "race")

    if name_like:
        df = races_df.loc[races_df.race_name.str.contains(name_like), :]
    else:
        df = races_df

    logger.info(f"List of races:\n {df.head(100)}")
    return df


def load_model(database_name):
    for object_name in ["team", "cyclist", "race"]:
        df = get_object(database_name, object_name)
        model_api.insert_pcm_object(database_name, object_name, df)


def get_database_file(database_name):
    database_file_name = f"{database_name}.sqlite"
    pcm_database_file = os.path.join(os.getcwd(), "src", "data", "pcm_dbs", database_file_name)
    return pcm_database_file


def validate_pcm_database(database_name):
    logger.info(f"Validating PCM database: '{database_name}'")
    database_file = get_database_file(database_name)
    if os.path.exists(database_file):
        logger.info(f"✅ PCM Database {database_name} exists at {database_file}")
        model_api.create_model()
        return True
    logger.info(f"❌ PCM Database {database_name} does not exist at {database_file}")
    return False

