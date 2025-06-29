import os
import sys
import pandas as pd
from tqdm import tqdm
from thefuzz import process, fuzz
from enum import Enum
from sqlalchemy import text

from scrapers import procyclingstats
from utils import database_helper
from pcm import pcm_api
from utils import logger_helper
from utils import commons

logger = logger_helper.get_logger(__name__)


APP_DATABASE_FILE = os.path.join("src", "data", "dbs", "app", "v01.sqlite")
APP_DATABASE_NAME = "pcm-startlist-generator"
SCRAPER_DATA_SOURCE = "procyclingstats"

# PostgreSQL configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{APP_DATABASE_FILE}')

def escape_text_sql(text):
    return text.replace("'", "''")  # Proper SQL escaping


class TableName(Enum):
    PCM_DATABASE = "tbl_pcm_databases"
    PCM_TEAM = "tbl_pcm_teams"
    PCM_RACE = "tbl_pcm_races"
    PCM_CYCLIST = "tbl_pcm_cyclists"
    START_LIST_CYCLISTS = "tbl_start_list_cyclists"
    START_LIST_FILES = "tbl_start_list_files"
    START_LIST_VIEW = "start_list_view"
    PCM_DATABASE_VIEW = "pcm_database_view"
    START_LISTS = "tbl_start_lists"
    TEAMS = "tbl_teams"
    START_LIST_RACES = "tbl_start_list_races"
    CYCLISTS = "tbl_cyclists"

class AppDatabase:
    """Interface to the application database."""
    def __init__(self, db_file=APP_DATABASE_FILE, db_url=None):
        self.db_file = db_file
        self.db_url = db_url or DATABASE_URL
        self.connection = None
        self.scraper = None
        self.is_postgresql = self.db_url.startswith('postgresql')
        
        if not self.is_postgresql:
            # Ensure directory exists for SQLite
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        
        self.connect()
        self.init_tables()

    def connect(self):
        if self.connection is None:
            self.connection = database_helper.get_database_connection(
                db_file=self.db_file if not self.is_postgresql else None,
                db_url=self.db_url if self.is_postgresql else None
            )

    def close(self):
        if self.connection:
            if hasattr(self.connection, 'dispose'):
                self.connection.dispose()
            else:
                self.connection.close()
            self.connection = None

    def init_scraper(self, race_year, race_name, start_list_url=None):
        if self.scraper is None:
            self.scraper = procyclingstats.ProCyclingStatsStartListScraper(race_year, race_name, start_list_url)

    def init_tables(self):
        """Create database tables - works for both SQLite and PostgreSQL"""
        if self.is_postgresql:
            self._init_postgresql_tables()
        else:
            self._init_sqlite_tables()

    def _init_postgresql_tables(self):
        """Initialize PostgreSQL tables"""
        logger.info("Initializing PostgreSQL tables...")
        with self.connection.connect() as conn:
            # PCM Tables
            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.PCM_DATABASE.value}(
                    id SERIAL PRIMARY KEY,
                    pcm_database_name TEXT NOT NULL,
                    pcm_version TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))

            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.PCM_CYCLIST.value} (
                    pcm_database_id INTEGER NOT NULL,
                    cyclist_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    cyclist_first_name TEXT NOT NULL,
                    cyclist_last_name TEXT NOT NULL,
                    FOREIGN KEY (pcm_database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.PCM_TEAM.value} (
                    pcm_database_id INTEGER NOT NULL,
                    team_id INTEGER NOT NULL,
                    team_name TEXT NOT NULL,
                    team_short_name TEXT NULL,
                    FOREIGN KEY (pcm_database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.PCM_RACE.value} (
                    pcm_database_id INTEGER NOT NULL,
                    race_id INTEGER NOT NULL,
                    race_name TEXT NOT NULL,
                    race_abbrreviation TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    FOREIGN KEY (pcm_database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            # Start list staging tables
            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.START_LIST_FILES.value}(
                    id SERIAL PRIMARY KEY,
                    data_source TEXT,
                    race_year INTEGER,
                    race_name TEXT,
                    url TEXT,
                    blob_content TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))

            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.START_LIST_CYCLISTS.value} (
                    id SERIAL PRIMARY KEY,
                    start_list_file_id INTEGER,
                    team_name TEXT,
                    cyclist_name TEXT,
                    cyclist_first_name TEXT,
                    cyclist_last_name TEXT,
                    FOREIGN KEY (start_list_file_id) REFERENCES {TableName.START_LIST_FILES.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            # App Final Tables
            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.START_LIST_RACES.value}(
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    pcm_race_id INTEGER NOT NULL,
                    pcm_database_id INTEGER NOT NULL,
                    FOREIGN KEY (pcm_database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.TEAMS.value}(
                    id SERIAL PRIMARY KEY,
                    start_list_race_id INTEGER,
                    pcm_team_id INTEGER,
                    team_name TEXT,
                    FOREIGN KEY (start_list_race_id) REFERENCES {TableName.START_LIST_RACES.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS {TableName.CYCLISTS.value}(
                    id SERIAL PRIMARY KEY,
                    team_id INTEGER,
                    pcm_cyclist_id INTEGER,
                    cyclist_name TEXT,
                    FOREIGN KEY (team_id) REFERENCES {TableName.TEAMS.value} (id)
                         ON DELETE CASCADE
                         ON UPDATE NO ACTION
                )
            '''))

            conn.execute(text(f'''
                CREATE VIEW {TableName.PCM_DATABASE_VIEW.value} AS
                SELECT d.id as pcm_database_id, r.race_id, r.race_name, t.team_id, t.team_name, c.cyclist_id, c.cyclist_first_name, c.cyclist_last_name
                FROM {TableName.PCM_DATABASE.value} d
                    INNER JOIN {TableName.PCM_RACE.value} r ON d.id = r.pcm_database_id
                    INNER JOIN {TableName.PCM_TEAM.value} t ON d.id = t.pcm_database_id
                    INNER JOIN {TableName.PCM_CYCLIST.value} c ON t.team_id = c.team_id
            '''))

            conn.execute(text(f'''
                CREATE VIEW {TableName.START_LIST_VIEW.value} AS
                SELECT d.id as pcm_database_id, d.pcm_database_name, d.pcm_version, r.year as race_year, r.pcm_race_id, r.name as race_name, t.pcm_team_id, t.team_name, c.pcm_cyclist_id, c.cyclist_name
                FROM {TableName.PCM_DATABASE.value} d
                    INNER JOIN  {TableName.START_LIST_RACES.value} r ON d.id = r.pcm_database_id
                    INNER JOIN {TableName.TEAMS.value} t ON r.id = t.start_list_race_id
                    INNER JOIN {TableName.CYCLISTS.value} c ON t.id = c.team_id
            '''))
        


    def import_pcm_data(self, pcm_version, pcm_database_name):
        """Fetches and stages the data from the PCM database.
        """
        
        # Create new row for the new PCM database
        db_table_name = TableName.PCM_DATABASE.value
        df = pd.DataFrame({
            "pcm_database_name": [pcm_database_name],
            "pcm_version": [pcm_version]
        })
        logger.info(f"Inserting row into table '{db_table_name}'")
        df.to_sql(
            name=db_table_name,
            con=self.connection,
            if_exists="append",
            index=False
        )

        pcm_database_id = self.get_pcm_database_id(pcm_version, pcm_database_name)
        pcm_db = pcm_api.PCMDatabase(pcm_database_name, pcm_version)
        for pcm_object in commons.PCMTableName:
            df = pcm_db.get_pcm_object(table_name=pcm_object.value)
            df["pcm_database_id"] = pcm_database_id
            object_name = f"PCM_{pcm_object.name.upper()}"
            self.insert_table(object_name, df)

        logger.info(f"✅ Imported PCM data for database '{pcm_database_name}' and PCM version '{pcm_version}' with pcm_database_id '{pcm_database_id}'")
        
    def insert_table(self, object_name, df):
        table_name = TableName[object_name].value
        logger.info(f"Inserting {len(df)} rows into table '{table_name}'")
        
        if self.is_postgresql:
            df.to_sql(
                name=table_name,
                con=self.connection,
                if_exists="append",
                index=False,
                method='multi'
            )
        else:
            df.to_sql(
                name=table_name,
                con=self.connection,
                if_exists="append",
                index=False
            )

    def get_start_list_data(self, pcm_database_id, pcm_race_id, race_year):
        query = f"""
            SELECT *
            FROM {TableName.START_LIST_VIEW.value}
            WHERE pcm_database_id = {pcm_database_id} AND pcm_race_id = {pcm_race_id} AND race_year = {race_year}
        """
        logger.debug(query)
        return pd.read_sql_query(query, self.connection)

    def does_start_list_exist(self, race_name, race_year):
        logger.info(f"Checking for Start Lists...")
        df = database_helper.run_query(self.connection, f"SELECT downloaded_at FROM stg_start_list_files WHERE race_name = '{escape_text_sql(race_name)}' AND race_year = {race_year} ORDER BY downloaded_at DESC")
        if len(df) > 0:
            last_downloaded_at = df['downloaded_at'].iloc[0]
            logger.info(f"✅ Start List for '{race_year} - {race_name}' is downloaded as of '{last_downloaded_at}'")
            df2 = database_helper.run_query(conn, f"SELECT * FROM stg_start_list_cyclists WHERE race_name = '{escape_text_sql(race_name)}' AND race_year = {race_year}")
            start_list_cyclists_count = len(df2)
            if start_list_cyclists_count > 100:
                logger.info(f"✅ {start_list_cyclists_count} Start List cyclists exist in database")
            else:
                logger.info(f"❌ Start List for '{race_year} - {race_name}' has been downloaded, but cyclist data not transformed")
                return False
            return True
        else:
            logger.info(f"❌ Start List for '{race_year} - {race_name}' has not been downloaded yet")
        return False

    def download_and_stage_start_list(self, race_year, start_list_race_name, start_list_url=None, fetch_from_web=False):
        """Downloads the start list from the web and inserts it into the database."""
        self.init_scraper(race_year=race_year, race_name=start_list_race_name, start_list_url=start_list_url)

        start_list_url, start_list_file_path_html = self.scraper.fetch_start_list(fetch_from_web=fetch_from_web)
            
        with open(start_list_file_path_html, "rb") as file:
            html_string = file.read().decode('utf-8')

        if html_string is None or html_string == "":
            logger.error(f"No start list raw data in file!")
            sys.exit(1)

        logger.info(f"Inserting Start List raw data into table '{race_year}' - '{start_list_race_name}' - '{start_list_url}' - '{SCRAPER_DATA_SOURCE}'")
        row_dict = {
            "data_source": [SCRAPER_DATA_SOURCE],
            "race_year": [race_year],
            "race_name": [start_list_race_name],
            "url": [start_list_url],
            "blob_content": [html_string],
        }

        df = pd.DataFrame.from_dict(row_dict)
        df.to_sql(
            name=TableName.START_LIST_FILES.value,
            con=self.connection,
            if_exists="append",
            index=False
        )
        
        rows = database_helper.run_query(self.connection, f"SELECT id FROM {TableName.START_LIST_FILES.value} WHERE race_year = {race_year} AND data_source = '{SCRAPER_DATA_SOURCE}' AND race_name = '{escape_text_sql(start_list_race_name)}' AND url = '{escape_text_sql(start_list_url)}' order by downloaded_at desc")
        start_list_file_id = rows[0]['id']
        logger.info(f"Added Start List html data into table '{TableName.START_LIST_FILES.value}' with id {start_list_file_id}")
        df = self.scraper.transform_raw_start_list(html_string)
        df['start_list_file_id'] = start_list_file_id

        df.to_sql(
            name=TableName.START_LIST_CYCLISTS.value,
            con=self.connection,
            if_exists="append",
            index=False
        )
        
        logger.info(f"Added {len(df)} Start List cyclists into table '{TableName.START_LIST_CYCLISTS.value}'")
        return start_list_file_id

    def match_start_list_and_pcm(self, pcm_database_id, start_list_file_id):
        """Matches PCM start list with the given PCM database ID and start list file ID."""

        def _match_start_list_cyclist_to_pcm(row, pcm_teams_cyclists_df):
            CONFIDENCE = 40
            team_name = row['team_name']
            sorted_cyclist_name = row['sorted_cyclist_name']
            cyclist_name = row['cyclist_name']

            # Get the best match for the team_name
            team_match = process.extractOne(team_name, pcm_teams_cyclists_df['team_name'], scorer=fuzz.token_sort_ratio)
            if team_match[1] < 80:  # if match score is below 80, consider it a poor match
                logger.error(f"Can't find match for team '{team_name}'")
                import pdb; pdb.set_trace()
                return pd.Series([None, None])

            matched_team_name = team_match[0]
            possible_matches = pcm_teams_cyclists_df[pcm_teams_cyclists_df['team_name'] == matched_team_name]

            # Get the best match for the cyclist name within the filtered team
            cyclist_name_match = process.extractOne(sorted_cyclist_name, possible_matches['sorted_cyclist_name'], scorer=fuzz.token_sort_ratio)

            if cyclist_name_match[1] >= CONFIDENCE:
                best_match = possible_matches[(possible_matches['sorted_cyclist_name'] == cyclist_name_match[0])]
                if not best_match.empty:
                    return pd.Series([best_match.iloc[0]['team_id'], best_match.iloc[0]['cyclist_id']])
            else:
                logger.error(f"Can't find match for cyclist '{cyclist_name}' with confidence {cyclist_name_match[1]} in team list:\n{possible_matches['sorted_cyclist_name'].tolist()}")
                return pd.Series([None, None])

            logger.error(f"Matched team '{matched_team_name}', but can't find match for '{cyclist_name}'")
            return pd.Series([matched_team_name, None])


        logger.info(f"Matching Start List (ID: {start_list_file_id}) with PCM Database (ID: {pcm_database_id})")
        get_start_list_sql = f"select team_name, cyclist_first_name || ' ' || cyclist_last_name as cyclist_name from {TableName.START_LIST_CYCLISTS.value} where start_list_file_id = {start_list_file_id}"

        logger.info(f"Fetching start list cyclists from file with id {start_list_file_id}")
        start_list_cyclists_df = pd.read_sql_query(get_start_list_sql, self.connection)
        
        if len(start_list_cyclists_df) == 0:
            logger.error(f"No start list cyclists found in start list file {start_list_file_id}")
            sys.exit(1)
        
        get_pcm_cyclists_sql = f"""
            select 
                CAST(t.team_id AS TEXT) as team_id,
                LOWER(t.team_name) as team_name,
                CAST(c.cyclist_id AS TEXT) as cyclist_id,
                LOWER(c.cyclist_first_name) || ' ' || LOWER(c.cyclist_last_name) as cyclist_name
            from {TableName.PCM_TEAM.value} t
                inner join {TableName.PCM_CYCLIST.value} c on t.team_id = c.team_id
            where t.pcm_database_id = {pcm_database_id}
        """
        logger.info(f"Fetching PCM cyclists from file with pcm_database_id {pcm_database_id}")

        pcm_teams_cyclists_df = pd.read_sql_query(get_pcm_cyclists_sql, self.connection)

        if len(pcm_teams_cyclists_df) == 0:
            logger.error(f"No PCM cyclists found in PCM database {pcm_database_id}")
            sys.exit(1)
        tqdm.pandas(desc='test')

        logger.info(f"Performing fuzzy matching cyclist name with {len(start_list_cyclists_df)} start list riders and {len(pcm_teams_cyclists_df)} pcm cyclists")

        def _sort_name(name):
            return ' '.join(sorted(name.split()))

        start_list_cyclists_df['sorted_cyclist_name'] = start_list_cyclists_df['cyclist_name'].apply(_sort_name)
        pcm_teams_cyclists_df['sorted_cyclist_name'] = pcm_teams_cyclists_df['cyclist_name'].apply(_sort_name)

        matched_df = start_list_cyclists_df.progress_apply(lambda row: _match_start_list_cyclist_to_pcm(row, pcm_teams_cyclists_df), axis=1)
        
        matched_df.columns = ['team_id', 'cyclist_id']
        final_df = pd.concat([start_list_cyclists_df, matched_df], axis=1)
        final_df = final_df.rename(columns={
            'team_id': 'pcm_team_id',
            'cyclist_id': 'pcm_cyclist_id'
        })
        unmatched_count = final_df['pcm_cyclist_id'].isnull().sum()
        logger.info(f"There are {unmatched_count} cyclists without matches ...")
        logger.info(f"{final_df[final_df['pcm_cyclist_id'].isnull()]}")

        return final_df
    
    def insert_start_list_race_data(self, df, pcm_database_id, pcm_race_id, race_name, race_year):
        """Inserts the start list riders into the database."""

        start_list_race_df = pd.DataFrame(
            {
                "pcm_database_id": [pcm_database_id], 
                "pcm_race_id": [pcm_race_id], 
                "name": [race_name], 
                "year": [race_year]
            }
        )

        logger.info(f"Inserting start list riders into table '{TableName.START_LIST_RACES.value}'")
        logger.info(f"\n{start_list_race_df}")

        start_list_race_df.to_sql(
            name=TableName.START_LIST_RACES.value,
            con=self.connection,
            if_exists="append",
            index=False
        )

        start_list_races_rows = database_helper.run_query(self.connection, f"SELECT id FROM {TableName.START_LIST_RACES.value} WHERE year = {race_year} AND name = '{race_name}' AND pcm_database_id = {pcm_database_id} AND pcm_race_id = {pcm_race_id} ORDER BY id DESC")
        start_list_race_id = start_list_races_rows[0]['id']

        insert_teams_df = df[['team_name', 'pcm_team_id']].drop_duplicates()
        insert_teams_df['start_list_race_id'] = start_list_race_id
        
        insert_teams_df.to_sql(
            name=TableName.TEAMS.value,
            con=self.connection,
            if_exists="append",
            index=False
        )
        logger.info(f"Inserted {len(insert_teams_df)} teams into the table '{TableName.TEAMS.value}'")
        
        teams_df = pd.read_sql_query(f"SELECT id as team_id, pcm_team_id from {TableName.TEAMS.value} WHERE start_list_race_id = {start_list_race_id}", self.connection)

        cyclists_df = df[['cyclist_name', 'pcm_cyclist_id', 'pcm_team_id']].drop_duplicates()
        
        # Convert pcm_team_id to integer for both dataframes to ensure compatibility
        cyclists_df['pcm_team_id'] = pd.to_numeric(cyclists_df['pcm_team_id'], errors='coerce').astype('Int64')
        teams_df['pcm_team_id'] = pd.to_numeric(teams_df['pcm_team_id'], errors='coerce').astype('Int64')
        
        # Join cyclists with teams to get the team_id
        cyclists_df = cyclists_df.merge(
            teams_df[['team_id', 'pcm_team_id']], 
            on='pcm_team_id', 
            how='left'
        )
        
        # Drop the pcm_team_id column as it's no longer needed
        cyclists_df = cyclists_df.drop('pcm_team_id', axis=1)

        cyclists_df.to_sql(
            name=TableName.CYCLISTS.value,
            con=self.connection,
            if_exists="append",
            index=False
        )

        logger.info(f"Inserted {len(cyclists_df)} cyclists into the table '{TableName.CYCLISTS.value}'")
        import pdb; pdb.set_trace()

    def get_pcm_databases(self, pcm_version=None):
        filter = ""
        if pcm_version:
            filter = f" WHERE pcm_version = {pcm_version}"

        df = pd.read_sql_query(f"SELECT id as pcm_database_id, pcm_version, created_at FROM {TableName.PCM_DATABASE.value} {filter} ORDER BY pcm_database_name", self.connection)
        return df

    def get_pcm_database_details(self, pcm_database_id):
        df = pd.read_sql_query(f"SELECT pcm_database_name, pcm_version FROM {TableName.PCM_DATABASE.value} WHERE id = {pcm_database_id}", self.connection)
        if df is None or len(df) == 0:
            logger.error(f"🚨 Could not find PCM database name for pcm_database_id={pcm_database_id}")
            return None
        return df['pcm_database_name'].iloc[0], df['pcm_version'].iloc[0] 

    def get_pcm_races(self, pcm_database_id, race_name=None):
        filter = f" WHERE pcm_database_id = {pcm_database_id}"
        if race_name:
            filter += f" and race_name LIKE '%{escape_text_sql(race_name)}%'"
        logger.info(f"Fetching PCM races with filter {filter}")
        df = pd.read_sql_query(f"SELECT * FROM {TableName.PCM_RACE.value} {filter} ORDER BY race_name", self.connection)
        return df

    def get_start_lists(self, pcm_version=None, pcm_database_name=None):
        filter = ""
        if pcm_version:
            filter += f" WHERE pcm_version = {pcm_version}"
        if pcm_database_name:
            if filter:
                filter += " AND"
            else:
                filter += " WHERE"
            filter += f" pcm_database_name = '{escape_text_sql(pcm_database_name)}'"
        df = pd.read_sql_query(f"SELECT pcm_database_id, pcm_version, pcm_database_name, race_name, race_year, count(*) FROM {TableName.START_LIST_VIEW.value} {filter} GROUP BY 1,2,3,4,5 ORDER BY pcm_database_name DESC, race_year DESC", self.connection)
        return df

    def get_pcm_race_details(self, pcm_database_id, pcm_race_id):
        results = database_helper.run_query(self.connection, f"SELECT race_id, LOWER(race_name) as race_name, file_name FROM {TableName.PCM_RACE.value} WHERE pcm_database_id = {pcm_database_id} and race_id = {pcm_race_id}")
        if results is None or len(results) == 0:
            logger.error(f"🚨 Could not find PCM start list file for pcm_database_id={pcm_database_id} and race_id={pcm_race_id}")
            return None
        file_name = f"{results[0]['file_name']}.xml"
        race_name = results[0]['race_name']
        return file_name, race_name

    def get_pcm_database_id(self, pcm_version, pcm_database_name):
        """Returns the database id for a given PCM version and database name."""
        sql_statement = f"SELECT id as pcm_database_id FROM {TableName.PCM_DATABASE.value} WHERE pcm_database_name = '{escape_text_sql(pcm_database_name)}' AND pcm_version = '{escape_text_sql(pcm_version)}' order by created_at desc"
        
        if self.is_postgresql:
            df = pd.read_sql_query(sql_statement, self.connection)
        else:
            df = pd.read_sql_query(sql_statement, self.connection)
        
        pcm_database_id = df['pcm_database_id'].iloc[0] if not df.empty else None
        return pcm_database_id