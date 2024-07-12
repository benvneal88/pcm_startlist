import os
from src.pcm import extract
from src.model import model_api
from src.utils import database_helper
from src.utils import logger_helper
logger = logger_helper.get_logger(__name__)


def load_model(database_name):
    for object_name in ["team", "cyclist", "race"]:
        df = extract.get_object(database_name, object_name)
        model_api.insert_pcm_object(database_name, object_name, df)


def join_start_list_to_pcm(startlist_df, cyclists_teams):
    logger.info(f"pcm:\n{cyclists_teams}")
    logger.info(f"startlist:\n{startlist_df}")

    for tuple in startlist_df.itertuples():
        rider_name = getattr(tuple, rider_name, None)

