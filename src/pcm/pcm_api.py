

import os
import sys
import pandas

import xml.etree.ElementTree as ET
from xml.dom import minidom

from utils import database_helper
from utils import logger_helper
import config
from utils import commons
logger = logger_helper.get_logger(__name__)


def get_xml_start_list(df):
    # Create the root element
    startlist = ET.Element('startlist')

    # Group the DataFrame by team ID
    grouped = df.groupby('pcm_team_id')

    # Iterate through each group
    for team_id, group in grouped:
        # Create a team element with the team ID
        team = ET.SubElement(startlist, 'team', id=str(team_id).replace('.0', ''))

        # Add cyclist elements for each cyclist in the team
        for cyclist_id in group['pcm_cyclist_id']:
            ET.SubElement(team, 'cyclist', id=str(cyclist_id).replace('.0', ''))

    # Convert the ElementTree to a string
    xml_str = ET.tostring(startlist, encoding='unicode')

    # Parse the string using minidom for pretty-printing
    xml_dom = minidom.parseString(xml_str)
    pretty_xml_str = xml_dom.toprettyxml(indent='    ')

    return pretty_xml_str



class PCMDatabase:
    def __init__(self, database_name, pcm_version):
        """Extracts the required data from the PCM database."""
        assert pcm_version in commons.PCM_VERSIONS
        self.pcm_version = pcm_version
        self.database_name = database_name
        self.database_file_path = os.path.join(os.getcwd(), commons.PCM_DATABASE_PATH, f"{self.database_name}.sqlite")
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
        
        database_field_mappings = commons.PCM_DATABASE_MAPPINGS.get(self.pcm_version)
        
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

