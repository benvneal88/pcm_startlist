import sys

from src.pcm import pcm_api
from src.model import model_api
from src.scrapers import procyclingstats
from src.utils import logger_helper
logger = logger_helper.get_logger(__name__)

# database_connection = pcm_api.get_database_file("worlddb_2024.sqlite")
#
# extract.get_object(database_connection, "race")
# races_filtered_df = extract.list_races(database_connection, name_like="Tour de France")
#
# race_id = int(races_filtered_df['race_id'].iloc[0])
#startlist_file_name = extract.get_race_startlist_file_name(race_id=race_id)

#cyclists_teams = extract.get_cyclists_teams()

#join_start_list_to_pcm(startlist_df, cyclists_teams)



def generate_start_list(pcm_database_name, race_name, year):

    # validate pcm database and race_name.
    if not pcm_api.validate_pcm_database(pcm_database_name):
        sys.exit(1)

    # extract data from the PCM database if needed
    if not model_api.check_for_pcm_data(pcm_database_name):
        pcm_api.load_model(pcm_database_name)

    file_name = model_api.check_for_pcm_race(pcm_database_name, race_name)
    start_list_xml_file_path = model_api.get_xml_file_path(file_name)

    # check for start list data. validate race_name. fetch html if needed. validate
    if not model_api.does_start_list_exist(race_name, year):
        scraper = procyclingstats.ProCyclingStatsStartListScraper(year, race_name)
        scraper.sync_start_list_to_database(refresh=False)

    df = model_api.get_start_list_data(pcm_database_name, race_name, year)

    # generate start list xml
    model_api.generate_xml_start_list(df, start_list_xml_file_path)
    logger.info(f"Place generated file into your PCM game directory: '%AppData%\Roaming\Pro Cycling Manager 2024\Cloud\Startlists\\'")
