import sys


from model import model_api
from scrapers import scraper_api
from utils import logger_helper
logger = logger_helper.get_logger(__name__)



def get_app():
    """Returns the app instance"""
    return model_api.AppDatabase()


def generate_start_list(
        pcm_database_name, 
        pcm_race_name, 
        race_name, 
        race_year, 
        pcm_version="2024", 
        force_start_list_refresh=False
    ):
    """Generates the start list XML
    
    :param pcm_database_name: The name of the PCM database
    :param pcm_race_name: The name of the PCM race
    :param pcm_version: The version of PCM video game
    :param race_name: The name of the race name from the start list source
    :param race_year: The year/edition of the race for fetching the start list
    """ 

    app = get_app()
    

    start_list_exists = app.check_for_start_list(pcm_version, pcm_database_name, race_name, race_year)
    
    # if the start list already exists, return the start list unless the user wants to force a refresh of the start list
    if force_start_list_refresh or not start_list_exists:
        app.download_and_insert_start_list(race_year, race_name)


    #start_list_xml_file_path = model_api.get_xml_file_path(file_name)
    # model_api.generate_xml_start_list(df, start_list_xml_file_path)
    # # check for start list data. validate race_name. fetch html if needed. validate

    

    # # generate start list xml
    # model_api.generate_xml_start_list(df, start_list_xml_file_path)
    # logger.info(f"Next step: copy generated file into your PCM game directory: '%AppData%\Roaming\Pro Cycling Manager 2024\Cloud\Startlists\'")


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
    for row in app.get_pcm_databases(pcm_version):
        print(f"database_id: {row['id']}, PCM Version: {row['pcm_version']}, Database Name: {row['pcm_database_name']}")
    app.close()


def show_start_lists(pcm_version=None, pcm_database_name=None):
    """Retrieves start lists that have been generated along with the pcm database name

    :return:
    """
    app = get_app()
    print(app.get_start_lists(pcm_version, pcm_database_name))  
    app.close()
