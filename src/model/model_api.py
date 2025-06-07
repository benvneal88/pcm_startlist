import os
import pandas as pd
from enum import Enum
from utils import database_helper
from pcm import pcm_api
from utils import logger_helper

logger = logger_helper.get_logger(__name__)


APP_DATABASE_FILE = os.path.join("src", "data", "dbs", "app", "v01.sqlite")
APP_DATABASE_NAME = "pcm-startlist-generator"

class TableName(Enum):
    PCM_DATABASE = "tbl_pcm_databases"
    PCM_TEAM = "tbl_pcm_teams"
    PCM_RACE = "tbl_pcm_races"
    PCM_CYCLIST = "tbl_pcm_cyclists"
    START_LIST_CYCLISTS = "tbl_start_list_cyclists"
    START_LIST_FILES = "tbl_start_list_files"

class AppDatabase:
    """Interface to the application database."""
    def __init__(self, db_file=APP_DATABASE_FILE):
        self.db_file = db_file
        self.connection = None
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self.connect()
        self.init_tables()

    def connect(self):
        if self.connection is None:
            self.connection = database_helper.get_database_connection(self.db_file)

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def init_tables(self):
        # Create app database if it doesn't exist
        cursor = self.connection.cursor()

        # PCM Tables
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TableName.PCM_DATABASE.value}(
                id integer PRIMARY KEY,
                pcm_database_name text NOT NULL,
                pcm_version text NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TableName.PCM_CYCLIST.value} (
                database_id INTEGER NOT NULL,
                cyclist_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                cyclist_first_name TEXT NOT NULL,
                cyclist_last_name TEXT NOT NULL,
                FOREIGN KEY (database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TableName.PCM_TEAM.value} (
                database_id INTEGER NOT NULL,
                team_id INTEGER NOT NULL,
                team_name TEXT NOT NULL,
                team_short_name TEXT NULL,
                FOREIGN KEY (database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TableName.PCM_RACE.value} (
                database_id INTEGER NOT NULL,
                race_id INTEGER NOT NULL,
                race_name TEXT NOT NULL,
                race_abbrreviation TEXT NOT NULL,
                file_name TEXT NOT NULL,
                FOREIGN KEY (database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')

        # Start list tables
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TableName.START_LIST_CYCLISTS.value} (
                race_year integer,
                race_name text,
                team_name text,
                cyclist_name text,
                cyclist_first_name text,
                cyclist_last_name text
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TableName.START_LIST_FILES.value}(
                data_source text,
                race_year integer,
                race_name text,
                url text,
                blob_content text,
                downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # App Final Tables

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS tbl_teams(
                id integer PRIMARY KEY,
                database_id integer,
                pcm_team_id integer,
                team_name text,
                team_shortname text,
                FOREIGN KEY (database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS tbl_races(
                id integer PRIMARY KEY,
                database_id integer NOT NULL,
                pcm_race_id integer NOT NULL,
                race_year integer NOT NULL,
                race_name text NOT NULL,
                race_abbrreviation text NULL,
                file_name text NOT NULL,
                FOREIGN KEY (database_id) REFERENCES {TableName.PCM_DATABASE.value} (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS tbl_cyclists(
                id integer PRIMARY KEY,
                team_id integer,
                pcm_cyclist_id integer,
                cyclist_name text,
                cyclist_last_name text,
                cyclist_first_name text,
                FOREIGN KEY (team_id) REFERENCES tbl_teams (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS tbl_cyclists_races_mtm(
                id integer PRIMARY KEY,
                race_id integer,
                cyclist_id integer,
                FOREIGN KEY (race_id) REFERENCES tbl_races (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION,
                FOREIGN KEY (cyclist_id) REFERENCES tbl_cyclists (id)
                     ON DELETE CASCADE
                     ON UPDATE NO ACTION
            )
        ''')

        cursor.execute(f'''
            CREATE VIEW IF NOT EXISTS pcm_database_view AS
            SELECT d.id as database_id, d.pcm_database_name, d.pcm_version, r.id as race_id, r.race_name, r.race_year, t.id as team_id, t.team_name, c.id as cyclist_id, c.cyclist_name
            FROM {TableName.PCM_DATABASE.value} d
                INNER JOIN tbl_pcm_races r ON d.id = r.database_id
                INNER JOIN tbl_pcm_teams t ON d.id = t.database_id
                INNER JOIN tbl_pcm_cyclists c ON t.id = c.team_id
        ''')

        cursor.execute(f'''
            CREATE VIEW IF NOT EXISTS start_list_view AS
            SELECT d.id as database_id, d.pcm_database_name, d.pcm_version, r.id as race_id, r.race_name, r.race_year, t.id as team_id, t.team_name, c.id as cyclist_id, c.cyclist_name
            FROM {TableName.PCM_DATABASE.value} d
                INNER JOIN tbl_races r ON d.id = r.database_id
                INNER JOIN tbl_teams t ON d.id = t.database_id 
                INNER JOIN tbl_cyclists c ON t.id = c.team_id
        ''')
        
        self.connection.commit()

    def drop_tables(self, tables):
        conn = self.connect()
        cursor = conn.cursor()
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table}')
        conn.commit()

    def escape_text_sql(self, text):
        return text.replace("'", " ")

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

        sql_statement = f"SELECT id as database_id FROM {db_table_name} WHERE pcm_database_name = '{self.escape_text_sql(pcm_database_name)}' AND pcm_version = '{self.escape_text_sql(pcm_version)}' order by created_at desc"
        df = pd.read_sql_query(sql_statement, self.connection)
        database_id = df['database_id'].iloc[0] if not df.empty else None
        if database_id is None:
            logger.error(f"❌ Failed to find database id for '{pcm_database_name}' with version '{pcm_version}'")
            return None
        
        pcm_db = pcm_api.PCMDatabase(pcm_database_name, pcm_version)
        for pcm_object in pcm_api.PCMTableName:
            df = pcm_db.get_pcm_object(table_name=pcm_object.value)
            df["database_id"] = database_id
            object_name = f"PCM_{pcm_object.name.upper()}"
            self.insert_table(object_name, df)

        logger.info(f"✅ Imported PCM data for '{pcm_database_name}' for PCM game version '{pcm_version}' and database id '{database_id}'")
        
    def insert_table(self, object_name, df):
        table_name = TableName[object_name].value
        logger.info(f"Inserting {len(df)} rows into table '{table_name}'")
        df.to_sql(
            name=table_name,
            con=self.connection,
            if_exists="append",
            index=False
        )

    def get_start_list_data(self, race_name, race_year):
        conn = self.connect()
        query = f"""
            SELECT team_name, cyclist_first_name || ' ' || cyclist_last_name AS cyclist_name
            FROM stg_start_list_cyclists
            WHERE race_name = '{self.escape_text_sql(race_name)}' AND race_year = {race_year}
        """
        logger.info(query)
        return database_helper.run_query(conn, query)

    def insert_start_list_files(self, df):
        conn = self.connect()
        df.to_sql(
            name="stg_start_list_files",
            con=conn,
            if_exists="append",
            index=False
        )
        logger.info("Added Start List raw data")
        print(database_helper.run_query(conn, "SELECT * FROM stg_start_list_files"))

    def insert_start_list_riders(self, df, race_name, race_year):
        logger.info(f"Deleting and inserting {len(df)} rows into stg_start_list_cyclists")
        conn = self.connect()
        delete_sql = f"DELETE FROM stg_start_list_cyclists WHERE race_year = {race_year} AND race_name = '{self.escape_text_sql(race_name)}'"
        logger.debug(f"Deleting existing data: '{delete_sql}'")
        cursor = conn.cursor()
        cursor.execute(delete_sql)
        conn.commit()
        df.to_sql(
            name="stg_start_list_cyclists",
            con=conn,
            if_exists="append",
            index=False
        )

    def does_start_list_exist(self, race_name, race_year):
        logger.info(f"Checking for Start Lists...")
        conn = self.connect()
        df = database_helper.run_query(conn, f"SELECT downloaded_at FROM stg_start_list_files WHERE race_name = '{self.escape_text_sql(race_name)}' AND race_year = {race_year} ORDER BY downloaded_at DESC")
        if len(df) > 0:
            last_downloaded_at = df['downloaded_at'].iloc[0]
            logger.info(f"✅ Start List for '{race_year} - {race_name}' is downloaded as of '{last_downloaded_at}'")
            df2 = database_helper.run_query(conn, f"SELECT * FROM stg_start_list_cyclists WHERE race_name = '{self.escape_text_sql(race_name)}' AND race_year = {race_year}")
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

    def get_start_list_raw_html(self, data_source, race_year, race_name):
        conn = self.connect()
        df = database_helper.run_query(conn, f"SELECT blob_content FROM stg_start_list_files WHERE data_source = '{data_source}' AND race_year = {race_year} AND race_name = '{self.escape_text_sql(race_name)}' ORDER BY downloaded_at DESC")
        return df["blob_content"].iloc[0] if not df.empty else None

    def get_race_list_races_raw_html(self, data_source, race_year):
        conn = self.connect()
        df = database_helper.run_query(conn, f"SELECT blob_content FROM stg_start_list_races_files WHERE data_source = '{data_source}' AND race_year = {race_year} ORDER BY downloaded_at DESC")
        return df["blob_content"].iloc[0] if not df.empty else None

    def check_for_start_list(self, pcm_version, pcm_database_name, race_name, race_year):
        conn = self.connect()
        df = database_helper.run_query(self.connection, f"SELECT * FROM start_list_view WHERE pcm_version = {pcm_version} AND pcm_database_name = '{self.escape_text_sql(pcm_database_name)}' AND race_name = '{race_name}' AND race_year = {race_year}") 
        if len(df) == 0:
            logger.info(f"❌ Start list does not exist yet")
            return False
        else:
            logger.info(f"✅ Found existing start list")
            return True

    def get_pcm_databases(self, pcm_version=None):
        filter = ""
        if pcm_version:
            filter = f" WHERE pcm_version = {pcm_version}"

        df = database_helper.run_query(self.connection, f"SELECT * FROM {TableName.PCM_DATABASE.value} {filter} ORDER BY pcm_database_name")
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
            filter += f" pcm_database_name = '{self.escape_text_sql(pcm_database_name)}'"
        df = database_helper.run_query(self.connection, f"SELECT database_id, pcm_version, pcm_database_name, race_name, race_year, count(*) FROM start_list_view {filter} GROUP BY 1,2,3,4,5 ORDER BY pcm_database_name DESC, race_year DESC")
        return df

    def does_pcm_database_exist(self, pcm_version, pcm_database_name):
        conn = self.connect()
        df = database_helper.run_query(conn, f"SELECT * FROM {TableName.PCM_DATABASE.value} WHERE pcm_database_name = '{self.escape_text_sql(pcm_database_name)}' AND pcm_version = {pcm_version}")
        if len(df) == 0:
            logger.info(f"❌ PCM database '{pcm_database_name}' not found in app database")
            return False
        elif len(df) > 1:
            logger.info(f"❌ More than one PCM database '{pcm_database_name}' found in app database")
            return False
        else:
            logger.info(f"✅ Found PCM database '{pcm_database_name}' in app database")
            return True

    def validate_race_name(self, pcm_version, pcm_database_name, race_name):
        df = database_helper.run_query(conn, f"SELECT race_id, LOWER(race_name) as race_name, file_name FROM pcm_stg_races")
        df = df.loc[df.race_name.str.contains(race_name), :]
        if len(df) == 0:
            logger.info(f"❌ Found no races in PCM from provided race name '{race_name}'. Check spelling!")
            return None
        elif len(df) == 1:
            found_race_id = df['race_id'].iloc[0]
            found_race_name = df['race_name'].iloc[0]
            found_file_name = df['file_name'].iloc[0]
        elif len(df) > 1:
            df_exact_match = df[df['race_name'] == race_name]
            if len(df_exact_match) == 0 or len(df_exact_match) > 1:
                found_races = df["race_name"].tolist()
                logger.info(f"❌ Found more than one race matching criteria '{race_name}' in PCM '{','.join(found_races)}'")
                return None
            else:
                found_race_id = df_exact_match['race_id'].iloc[0]
                found_race_name = df_exact_match['race_name'].iloc[0]
                found_file_name = df_exact_match['file_name'].iloc[0]
        logger.info(f"✅ Found race '{found_race_name}' in PCM with id '{found_race_id}' and file_name '{found_file_name}'")
        return found_file_name