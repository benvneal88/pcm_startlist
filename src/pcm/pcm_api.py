import os
from pcm import extract
from utils import database_helper
from utils import logger_helper
logger = logger_helper.get_logger(__name__)

def get_database_file(database_name):
    pcm_database_file = os.path.join("data", "pcm_dbs", database_name)
    return database_helper.get_database_connection(pcm_database_file)

def load_model(database_name):
    pcm_database_file = get_database_file(database_name)
    database_connection = database_helper.get_database_connection(pcm_database_file)
    return extract.get_object(database_connection, "team")

def join_start_list_to_pcm(startlist_df, cyclists_teams):
    logger.info(f"pcm:\n{cyclists_teams}")
    logger.info(f"startlist:\n{startlist_df}")

    for tuple in startlist_df.itertuples():
        rider_name = getattr(tuple, rider_name, None)

