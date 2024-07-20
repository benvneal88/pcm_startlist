import os
import sys

import pandas as pd
from tqdm import tqdm
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import xml.etree.ElementTree as ET
from xml.dom import minidom
from src.utils import logger_helper
from src.utils import database_helper
logger = logger_helper.get_logger(__name__)

APP_DATABASE_FILE_NAME = "pcm_startlist.db"

APP_DATABASE_FILE = os.path.join(os.getcwd(), "src", "data", "app_dbs", APP_DATABASE_FILE_NAME)

OBJECT_TABLE_MAPPING = {
    "team": "pcm_stg_teams",
    "race": "pcm_stg_races",
    "cyclist": "pcm_stg_cyclists",
}


def escape_text_sql(text):
    text = text.replace("'", " ")
    return text


def match_dataframes(df1, df2):
    def sort_name(name):
        return ' '.join(sorted(name.split()))

    df1['sorted_name'] = df1['name'].apply(sort_name)
    df2['sorted_name'] = df2['name'].apply(sort_name)

    def get_best_match(row, choices):
        name = row['sorted_name']
        best_match = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
        return best_match[0] if best_match[1] >= 80 else None  # threshold of 80 for a good match

    df1['best_match'] = df1.apply(lambda row: get_best_match(row, df2['sorted_name'].tolist()), axis=1)

    df1.set_index('sorted_names', inplace=True)
    df2.set_index('sorted_names', inplace=True)

    matched_df = df2.join(df1, on='best_match', rsuffix='_df1')

    matched_df.reset_index(inplace=True)
    df1.reset_index(inplace=True)
    df2.reset_index(inplace=True)

    matched_df.drop(columns=['best_match'], inplace=True)

    return matched_df


def get_start_list_data(pcm_database_name, race_name, race_year):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    #get_start_list_sql = f"select team_name, cyclist_first_name, cyclist_last_name from stg_start_list_cyclists where race_name = '{escape_text_sql(race_name)}' and race_year = {race_year}"
    get_start_list_sql = f"select team_name, cyclist_first_name || ' ' || cyclist_last_name as cyclist_name from stg_start_list_cyclists where race_name = '{escape_text_sql(race_name)}' and race_year = {race_year}"
    logger.info(get_start_list_sql)
    start_list_cyclists_df = database_helper.run_query(database_connection, get_start_list_sql)
    #
    #
    # if len(start_list_cyclists_df) > 0:
    #     logger.error("No ")
    #     sys.exit(1)

    get_teams_cyclists_sql = f"""
        select 
            CAST(t.team_id AS TEXT) as team_id,
            LOWER(t.team_name) as team_name,
            CAST(c.cyclist_id AS TEXT) as cyclist_id,
            LOWER(c.cyclist_first_name) || ' ' || LOWER(c.cyclist_last_name) as cyclist_name
            --LOWER(c.cyclist_first_name) as cyclist_first_name,
            --LOWER(c.cyclist_last_name) as cyclist_last_name
        from pcm_stg_teams t 
            inner join pcm_stg_cyclists c on t.team_id = c.team_id
        where t.database_name = '{pcm_database_name}' 
            and c.database_name = '{pcm_database_name}'
    """
    pcm_teams_cyclists_df = database_helper.run_query(database_connection, get_teams_cyclists_sql)
    # import pdb;
    # pdb.set_trace()

    final_df = fuzzy_join(start_list_df=start_list_cyclists_df, pcm_roster_df=pcm_teams_cyclists_df)

    validate_start_list_df(start_list_df=start_list_cyclists_df, pcm_df=pcm_teams_cyclists_df, final_df=final_df)

    return final_df


def fuzzy_match(row, roster_df):
    team_name = row['team_name']
    sorted_cyclist_name = row['sorted_cyclist_name']
    cyclist_name = row['cyclist_name']

    if 'red bull' in team_name:
        team_name = team_name.replace("red bull ", "")

    # Get the best match for the team_name
    team_match = process.extractOne(team_name, roster_df['team_name'], scorer=fuzz.token_sort_ratio)
    if team_match[1] < 80:  # if match score is below 80, consider it a poor match
        logger.error(f"Can't find match for team '{team_name}'")
        return pd.Series([None, None])

    matched_team_name = team_match[0]
    possible_matches = roster_df[roster_df['team_name'] == matched_team_name]

    # Get the best match for the cyclist name within the filtered team
    cyclist_name_match = process.extractOne(sorted_cyclist_name, possible_matches['sorted_cyclist_name'], scorer=fuzz.token_sort_ratio)

    if cyclist_name_match[1] >= 50:
        best_match = possible_matches[(possible_matches['sorted_cyclist_name'] == cyclist_name_match[0])]
        if not best_match.empty:
            return pd.Series([best_match.iloc[0]['team_id'], best_match.iloc[0]['cyclist_id']])
    else:
        logger.error(f"Can't find match for cyclist '{cyclist_name}' with confidence {cyclist_name_match[1]} in team list:\n{possible_matches['sorted_cyclist_name'].tolist()}")
        return pd.Series([None, None])

    logger.error(f"Matched team '{matched_team_name}', but can't find match for '{cyclist_name}'")
    return pd.Series([matched_team_name, None])


def fuzzy_join(start_list_df, pcm_roster_df):
    tqdm.pandas()
    start_list_count = len(start_list_df)
    pcm_roster_count = len(pcm_roster_df)
    logger.info(f"Performing fuzzy matching team name, and cyclist name with {start_list_count} start list riders and {pcm_roster_count} pcm cyclists")

    def sort_name(name):
        return ' '.join(sorted(name.split()))

    start_list_df['sorted_cyclist_name'] = start_list_df['cyclist_name'].apply(sort_name)
    pcm_roster_df['sorted_cyclist_name'] = pcm_roster_df['cyclist_name'].apply(sort_name)

    matched_df = start_list_df.progress_apply(lambda row: fuzzy_match(row, pcm_roster_df), axis=1)
    matched_df.columns = ['team_id', 'cyclist_id']
    return pd.concat([start_list_df, matched_df], axis=1)


def validate_start_list_df(start_list_df, pcm_df, final_df):
    logger.info(f"Validating start list data...")
    logger.info(f"Source record count: {len(start_list_df)}")

    unmatched_count = final_df['cyclist_id'].isnull().sum()
    logger.info(f"There are {unmatched_count} cyclists without matches ...")
    logger.info(f"{final_df[final_df['cyclist_id'].isnull()]}")



def generate_xml_start_list(df, out_file):
    # Create the root element
    startlist = ET.Element('startlist')

    # Group the DataFrame by team ID
    grouped = df.groupby('team_id')

    # Iterate through each group
    for team_id, group in grouped:
        # Create a team element with the team ID
        team = ET.SubElement(startlist, 'team', id=str(team_id))

        # Add cyclist elements for each cyclist in the team
        for cyclist_id in group['cyclist_id']:
            ET.SubElement(team, 'cyclist', id=str(cyclist_id))

    # Convert the ElementTree to a string
    xml_str = ET.tostring(startlist, encoding='unicode')

    # Parse the string using minidom for pretty-printing
    xml_dom = minidom.parseString(xml_str)
    pretty_xml_str = xml_dom.toprettyxml(indent='    ')

    with open(out_file, "w") as f:
        f.write(pretty_xml_str)

    logger.info(f"🎉 Created XML Start List at {out_file}")


def get_xml_file_path(start_list_xml_file_name):
    file_path = os.path.join(os.getcwd(), "src", "data", "pcm_start_lists", f"{start_list_xml_file_name}.xml")
    return file_path


def create_model():
    # Open and read the file as a single buffer
    logger.info(f"Creating model tables as needed...")
    create_model_sql_file_path = os.path.join(os.getcwd(), "src", "model", "create_model.sql")
    try:
        with open(create_model_sql_file_path, 'r') as file:
            create_model_sql = file.read()
    except Exception as e:
        logger.error(f"Failed to open file '{create_model_sql_file_path}'")
        logger.exception(e)

    create_tables_sql = create_model_sql.split(';')

    conn = database_helper.get_database_connection(APP_DATABASE_FILE)
    # Execute every command from the input file
    for create_table_sql in create_tables_sql:
        logger.debug(f"Executing DDL:\n {create_table_sql}")
        try:
            conn.execute(create_table_sql)
        except Exception as e:
            print(e)


def delete_model_tables(drop_tables):
    conn = database_helper.get_database_connection(APP_DATABASE_FILE)
    database_helper.drop_tables(conn, drop_tables)


def check_for_pcm_data(pcm_database_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)

    tables_to_check_dict = {
        "pcm_stg_teams": {"minimum_count": 30},
        "pcm_stg_races": {"minimum_count": 50},
        "pcm_stg_cyclists": {"minimum_count": 10000},
    }

    for table_name, validation_config in tables_to_check_dict.items():
        df = database_helper.run_query(database_connection, f"select * from {table_name}")
        df_len = len(df)
        if df_len > validation_config.get("minimum_count", 10):
            logger.info(f"\t ✅ Table '{table_name}' contains {df_len} rows for PCM database {pcm_database_name}")
        else:
            logger.info(f"\t ❌ Table '{table_name}' contains {df_len} for PCM database {pcm_database_name}")
            return False
    logger.info(f"✅ Model already populated with data from this PCM Database!")
    return True


def check_for_pcm_race(pcm_database_name, race_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    logger.info(f"Checking PCM for race with name '{race_name}' and database_name '{pcm_database_name}'")
    df = database_helper.run_query(database_connection, f"select race_id, LOWER(race_name) as race_name, filename from pcm_stg_races") #{OBJECT_TABLE_MAPPING.get('race')}
    #import pdb; pdb.set_trace()
    df = df.loc[df.race_name.str.contains(race_name), :]
    if len(df) == 0:
        logger.info(f"❌ Found no races in PCM from provided race name '{race_name}'. Check spelling!")
        return None
    elif len(df) == 1:
        found_race_id = df['race_id'].iloc[0]
        found_race_name = df['race_name'].iloc[0]
        found_file_name = df['filename'].iloc[0]
    elif len(df) > 1:
        #if more than one race is found attempt attempt an exact filter
        df_exact_match = df[df['race_name'] == race_name]
        if len(df_exact_match) == 0 or len(df_exact_match) > 1:
            found_races = df["race_name"].tolist()
            logger.info(f"❌ Found more than one race matching criteria '{race_name}' in PCM '{','.join(found_races)}'")
            return None
        else:
            found_race_id = df_exact_match['race_id'].iloc[0]
            found_race_name = df_exact_match['race_name'].iloc[0]
            found_file_name = df_exact_match['filename'].iloc[0]

    logger.info(f"✅ Found race '{found_race_name}' in PCM with id '{found_race_id}' and file_name '{found_file_name}'")
    return found_file_name



def delete_old_pcm_data(pcm_database_name, table_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    delete_sql = f"delete from {table_name} where database_name = '{pcm_database_name}'"
    logger.info(f"Deleting existing data: '{delete_sql}'")
    cursor = database_connection.cursor()
    cursor.execute(delete_sql)
    database_connection.commit()


def insert_pcm_object(pcm_database_name, object_name, df):
    assert object_name in OBJECT_TABLE_MAPPING.keys()
    table_name = OBJECT_TABLE_MAPPING.get(object_name)
    delete_old_pcm_data(pcm_database_name, table_name)
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    logger.info(f"Inserting {len(df)} rows into table '{table_name}'")
    df.to_sql(
        name=table_name,
        con=database_connection,
        if_exists="append",
        index=False
    )
    database_connection.close()


def insert_start_list_files(df):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    df.to_sql(
        name="stg_start_list_files",
        con=database_helper.get_database_connection(APP_DATABASE_FILE),
        if_exists="append",
        index=False
    )
    logger.info("Added Start List raw data")

    print(database_helper.run_query(database_connection, "select * from stg_start_list_files"))
    database_connection.close()


def insert_start_list_riders(df, race_name, race_year):
    logger.info(f"Deleting and inserting {len(df)} rows into stg_start_list_cyclists")
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    delete_sql = f"delete from stg_start_list_cyclists where race_year = {race_year} and race_name = '{escape_text_sql(race_name)}'"
    logger.debug(f"Deleting existing data: '{delete_sql}'")
    cursor = database_connection.cursor()
    cursor.execute(delete_sql)
    database_connection.commit()
    df.to_sql(
        name="stg_start_list_cyclists",
        con=database_connection,
        if_exists="append",
        index=False
    )
    database_connection.close()


def does_start_list_exist(race_name, race_year):
    logger.info(f"Checking for Start Lists...")
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)

    df = database_helper.run_query(database_connection, f"select downloaded_at from stg_start_list_files where race_name = '{escape_text_sql(race_name)}' and race_year = {race_year} order by downloaded_at desc")
    if len(df) > 0:
        last_downloaded_at = df['downloaded_at'].iloc[0]
        logger.info(f"✅ Start List for '{race_year} - {race_name}' is downloaded as of '{last_downloaded_at}'")

        df = database_helper.run_query(database_connection,f"select * from stg_start_list_cyclists where race_name = '{escape_text_sql(race_name)}' and race_year = {race_year}")
        start_list_cyclists_count = len(df)
        if start_list_cyclists_count > 100:
            logger.info(f"✅ {start_list_cyclists_count} Start List cyclists exist in database")
        else:
            logger.info(f"❌ Start List for '{race_year} - {race_name}' has been downloaded, but cyclist data not transformed")
            return False
        return True
    else:
        logger.info(f"❌ Start List for '{race_year} - {race_name}' has not been downloaded yet")
    return False


def get_start_list_raw_html(data_source, race_year, race_name):
    database_connection = database_helper.get_database_connection(APP_DATABASE_FILE)
    df = database_helper.run_query(database_connection, f"select blob_content from stg_start_list_files where data_source = '{data_source}' and race_year = {race_year} and race_name = '{escape_text_sql(race_name)}' order by downloaded_at desc")
    return df["blob_content"].iloc[0]
