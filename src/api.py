import sys

from src.pcm import pcm_api
from src.model import model_api
from src.scrapers import procyclingstats
from src.utils import logger_helper
logger = logger_helper.get_logger(__name__)


def generate_start_list(pcm_database_name, race_name, race_year, pcm_version="2024"):
    # validate pcm database and race_name.
    if not pcm_api.validate_pcm_database(pcm_database_name):
        sys.exit(1)

    # extract data from the PCM database if needed
    if not model_api.check_for_pcm_data(pcm_database_name):
        pcm_api.load_model(pcm_database_name, pcm_version)

    # get start list file name
    file_name = model_api.check_for_pcm_race(pcm_database_name, race_name)
    if file_name is None:
        sys.exit(1)

    start_list_xml_file_path = model_api.get_xml_file_path(file_name)

    # check for start list data. validate race_name. fetch html if needed. validate
    if not model_api.does_start_list_exist(race_name, race_year):
        scraper = procyclingstats.ProCyclingStatsStartListScraper(race_year, race_name)
        scraper.insert_start_list_raw(fetch_from_web=False)
        scraper.insert_start_list_cyclists()
        
    df = model_api.get_start_list_data(pcm_database_name, race_name, race_year)

    # generate start list xml
    model_api.generate_xml_start_list(df, start_list_xml_file_path)
    logger.info(f"Next step: copy generated file into your PCM game directory: '%AppData%\Roaming\Pro Cycling Manager 2024\Cloud\Startlists\'")


def show_start_lists():
    """Retrieves start lists that have been downloaded

    :return:
    """
    pass

def show_pcm_databases():
    """Retrieves PCM databases that have been added

    :return:
    """
    pass

def show_pcm_start_lists():
    """Retrieves PCM databases that have been added

    :return:
    """
    pass