from src.src import extract
from src.src import pcm_api

database_connection = pcm_api.get_database_file("worlddb_2024.sqlite")

extract.get_object(database_connection, "race")
races_filtered_df = extract.list_races(database_connection, name_like="Tour de France")

race_id = int(races_filtered_df['race_id'].iloc[0])
#startlist_file_name = extract.get_race_startlist_file_name(race_id=race_id)

#cyclists_teams = extract.get_cyclists_teams()

#join_start_list_to_pcm(startlist_df, cyclists_teams)
