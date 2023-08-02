import os
import pcm_extract

from model import api as model_api

from utils import logger
logger = logger.get_logger_init()



if __name__ == "__main__":
    model_api.create_model()

    #model_api.drop_all_tables(conn)
    #print(model_api.list_tables())
    # url = "https://www.procyclingstats.com/race/tour-de-france/2023/start_list/start_list"
    # file_name = "start_list_tdf_2023.html"
    #
    # races_filtered_df = pcm_model.list_races(name_like="Tour de France")
    #
    # race_id = int(races_filtered_df['race_id'].iloc[0])
    # start_list_file_name = pcm_model.get_race_start_list_file_name(race_id=race_id)
    # start_list_df = scraper.get_start_list_from_url(url, file_name)
    # cyclists_teams = pcm_model.get_cyclists_teams()
    #
    # join_start_list_to_pcm(start_list_df, cyclists_teams)
