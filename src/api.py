import sys

from pcm import pcm_api
from model import model_api
from scrapers import scraper_api
from utils import logger_helper
logger = logger_helper.get_logger(__name__)



def get_app():
    """Returns the app instance"""
    return model_api.AppDatabase()


def generate_start_list(
        pcm_database_id,
        pcm_race_id,
        race_year,
        start_list_race_name=None,
        start_list_url=None,
        force_start_list_refresh=False
    ):
    """Generates the start list XML
    
    :param pcm_database_id: The ID of the imported PCM database to use
    :param pcm_race_id: The ID of the PCM race to generate the start list for
    :param race_year: The year/edition of the race for fetching the start list
    :param start_list_race_name: Force the start list lookup for a specific name (optional)
    :param start_list_url: Force the start list lookup for a specific url. (optional)
    :force_start_list_refresh: If True, forces fetching the start list from the internet even if it already exists
    """ 

    app = get_app()

    pcm_start_list_file_name, race_name = app.get_pcm_race_details(pcm_database_id, pcm_race_id)
    start_list_race_name = start_list_race_name if start_list_race_name else race_name

    df = app.get_start_list_data(pcm_database_id, pcm_race_id, race_year)
    
    start_list_exists = False
    if df.size > 0:
        start_list_exists = True

    # if the start list already exists, return the start list unless the user wants to force a refresh of the start list
    if force_start_list_refresh or not start_list_exists:
        start_list_file_id = app.download_and_stage_start_list(race_year, start_list_race_name, start_list_url)
        final_df = app.match_start_list_and_pcm(pcm_database_id, start_list_file_id)
        app.insert_start_list_race_data(final_df, pcm_database_id, pcm_race_id, race_name, race_year)
        df = app.get_start_list_data(pcm_database_id, pcm_race_id, race_year)
    else:
        logger.info(f"Found existing start list for '{start_list_race_name}' and year ({race_year})")

    pcm_database_name, pcm_version = app.get_pcm_database_details(pcm_database_id)
    app.close()
    
    pcm_api.generate_xml_start_list(df, pcm_version, pcm_database_name, race_year, pcm_start_list_file_name)
    
    logger.info(f"Next step: copy generated file into your PCM game directory: '%AppData%\Roaming\Pro Cycling Manager {pcm_version}\Cloud\Startlists\'")


def import_pcm_database(pcm_version, pcm_database_name):
    """Loads the PCM database into the app instance

    :param pcm_database_name: The name of the PCM database
    :param pcm_version: The version of PCM video game
    """
    app = get_app()
    app.import_pcm_data(pcm_version, pcm_database_name)
    app.close()


def show_pcm_databases(pcm_version=None):
    """Retrieves PCM databases that have been loaded

    :return:
    """
    app = get_app()
    logger.info(f"\n{app.get_pcm_databases(pcm_version)}")
    app.close()


def show_pcm_races(pcm_database_id, race_name=None):
    """Retrieves PCM races
    :return:
    """
    app = get_app()
    logger.info(f"\n{app.get_pcm_races(pcm_database_id, race_name=race_name)}")
    app.close()


def show_start_lists(pcm_version=None, pcm_database_name=None):
    """Retrieves start lists that have been generated along with the pcm database name

    :return:
    """
    app = get_app()
    print(app.get_start_lists(pcm_version, pcm_database_name))  
    app.close()
