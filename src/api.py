import pcm_model
import scraper
import utils

logger = utils.get_logger_init()


def join_start_list_to_pcm(startlist_df, cyclists_teams):
    logger.info(f"pcm:\n{cyclists_teams}")
    logger.info(f"startlist:\n{startlist_df}")

    for tuple in startlist_df.itertuples():
        rider_name = getattr(tuple, rider_name, None)



if __name__ == "__main__":
    url = "https://www.procyclingstats.com/race/tour-de-france/2023/startlist/startlist"
    file_name = "startlist_tdf_2023.html"

    races_filtered_df = pcm_model.list_races(name_like="Tour de France")

    race_id = int(races_filtered_df['race_id'].iloc[0])
    startlist_file_name = pcm_model.get_race_startlist_file_name(race_id=race_id)
    startlist_df = scraper.get_startlist_from_url(url, file_name)
    cyclists_teams = pcm_model.get_cyclists_teams()

    join_start_list_to_pcm(startlist_df, cyclists_teams)
