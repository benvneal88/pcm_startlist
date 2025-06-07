from enum import Enum
import os
import sys
import pandas

from utils import database_helper
from utils import logger_helper
import config
logger = logger_helper.get_logger(__name__)

PCM_DATABASE_PATH = os.path.join("src", "data", "dbs", "pcm")

class PCMTableName(Enum):
    TEAM = "DYN_team"
    RACE = "STA_race"
    CYCLIST = "DYN_cyclist"


class PCMVersion(Enum):
    V2025 = "2025"
    V2024 = "2024"
    V2023 = "2023"


PCM_DATABASE_FIELD_MAPPINGS = {
    "2025":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        },
    "2024":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        },
    "2023":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        }
}


class PCMDatabase:
    def __init__(self, database_name, pcm_version=PCMVersion.V2024.value):
        """Extracts the required data from the PCM database."""
        assert pcm_version in [i.value for i in PCMVersion]
        self.pcm_version = pcm_version
        self.database_name = database_name
        self.database_file_path = os.path.join(os.getcwd(), PCM_DATABASE_PATH, f"{self.database_name}.sqlite")
        if self.database_file_exists():
            self.connection = database_helper.get_database_connection(self.database_file_path)
        else:
            sys.exit(1)

    def database_file_exists(self):
        if os.path.exists(self.database_file_path):
            logger.info(f"✅ PCM Database {self.database_name} exists at {self.database_file_path}")
            return True
        logger.info(f"❌ PCM Database {self.database_name} does not exist at {self.database_file_path}")
        return False

    def close_connection(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_pcm_object(self, table_name):
        """Fetches the data from the PCM database."""
        
        database_field_mappings = PCM_DATABASE_FIELD_MAPPINGS.get(self.pcm_version)
        
        table_field_mappings = database_field_mappings.get(table_name)
        if table_field_mappings is None:
            logger.error(f"Table {table_name} not found in database field mappings")
            return None
    
        table_columns = database_helper.get_columns(self.connection, table_name)
        for column_name in table_field_mappings.keys():
            if column_name not in table_columns:
                logger.error(f"Column {column_name} not found in table")

        columns_select_statements = []
        for column_name, rename_to in table_field_mappings.items():
            columns_select_statements.append(f"{column_name} as {rename_to}")

        select_statement = ",".join(columns_select_statements)

        sql_statement = f"SELECT {select_statement} FROM {table_name}"
        logger.info(f"SQL Statement: '{sql_statement}'")
        
        df = pandas.read_sql_query(sql_statement, self.connection)

        return df

