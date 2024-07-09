
from utils import logger_helper
from model import api as model_api

logger = logger_helper.get_logger(__name__)

MODEL_DB_FILE = "model/database.sqlite"

def create_model(database_connection):
    # Open and read the file as a single buffer
    with open("model/create_model.sql", 'r') as file:
        create_model_sql = file.read()

    create_tables_sql = create_model_sql.split(';')

    # Execute every command from the input file
    for create_table_sql in create_tables_sql:
        try:
            conn.execute(create_table_sql)
        except Exception as e:
            print(e)

def join_start_list_to_pcm(startlist_df, cyclists_teams):
    logger.info(f"pcm:\n{cyclists_teams}")
    logger.info(f"startlist:\n{startlist_df}")

    for tuple in startlist_df.itertuples():
        rider_name = getattr(tuple, rider_name, None)



if __name__ == "__main__":
    conn = model_api.get_database_conn(MODEL_DB_FILE)
    #create_model(conn)

    #model_api.drop_all_tables(conn)
    print(model_api.list_tables(conn))
    # url = "https://www.procyclingstats.com/race/tour-de-france/2023/startlist/startlist"
    # file_name = "startlist_tdf_2023.html"
    #
    # races_filtered_df = pcm_model.list_races(name_like="Tour de France")
    #
    # race_id = int(races_filtered_df['race_id'].iloc[0])
    # startlist_file_name = pcm_model.get_race_startlist_file_name(race_id=race_id)
    # startlist_df = scraper.get_startlist_from_url(url, file_name)
    # cyclists_teams = pcm_model.get_cyclists_teams()
    #
    # join_start_list_to_pcm(startlist_df, cyclists_teams)
