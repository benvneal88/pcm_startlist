import sys
import os
import pandas as pd

from pcm import pcm_api
from model import model_api
from scrapers import scraper_api
from utils import logger_helper, commons

logger = logger_helper.get_logger(__name__)

class AppAPI():
    """API for interacting with the PCM Start List Generator application"""
    
    def __init__(self):
        self.app_model = model_api.AppDatabase(db_url=os.getenv('DATABASE_URL'))
        pd.set_option('display.max_columns', None)

    def close(self):
        """Close the app instance"""
        self.app_model.close()

    def get_start_list_output_file_path(self, pcm_database_id, pcm_race_id, race_year):
        """Retrieves the file path for the generated start list

        :param pcm_database_id: The ID of the imported PCM database to use
        :param pcm_race_id: The ID of the PCM race to generate the start list for
        :param race_year: The year/edition of the race for fetching the start list
        :return: The file path of the raw start list
        """
        race_df = self.app_model.get_race(pcm_database_id, pcm_race_id)
        pcm_database_name, pcm_version = self.app_model.get_pcm_database_details(pcm_database_id)
        return os.path.join(commons.START_LIST_OUTPUT_PATH, pcm_version, pcm_database_name, str(race_year), f"{race_df.iloc[0]['file_name']}.xml")

    def generate_start_list(
            self,
            pcm_database_id,
            pcm_race_id,
            race_year,
            force_start_list_race_name=None,
            force_start_list_url=None
        ):
        """Generates the start list XML
        
        :param pcm_database_id: The ID of the imported PCM database to use
        :param pcm_race_id: The ID of the PCM race to generate the start list for
        :param race_year: The year/edition of the race for fetching the start list
        :param force_start_list_race_namestart_list_race_name: Force the start list lookup for a specific name (optional)
        :param force_start_list_url: Force the start list lookup for a specific url. (optional)
        """ 

        race_df = self.app_model.get_race(pcm_database_id, pcm_race_id)
        start_list_race_name = force_start_list_race_name if force_start_list_race_name else race_df.iloc[0]['start_list_race_name']

        start_list_file_id, start_list_downloaded_at, start_list_url = self.app_model.download_and_stage_start_list(race_year, start_list_race_name, force_start_list_url)
        if start_list_file_id is None:
            return None, start_list_url
        
        final_df = self.app_model.match_start_list_and_pcm(pcm_database_id, start_list_file_id)
        start_list_race_id = self.app_model.insert_start_list_race_data(final_df, pcm_database_id, pcm_race_id, race_df.iloc[0]['pcm_race_name'], race_year, start_list_downloaded_at)
        df = self.app_model.get_start_list_data(start_list_race_id)

        pcm_database_name, pcm_version = self.app_model.get_pcm_database_details(pcm_database_id)
        
        xml_data = pcm_api.get_xml_start_list(df)
        out_path = self.get_start_list_output_file_path(pcm_database_id, pcm_race_id, race_year)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(xml_data)

        logger.info(f"🎉 Created XML Start List at {out_path}")
        pcm_year = pcm_version.replace("PCM_","")
        logger.info(f"Next step: copy generated file into your PCM game directory: '%AppData%\Roaming\Pro Cycling Manager {pcm_year}\Cloud\Startlists\'")
        return out_path, start_list_url 

    def download_start_list(self, start_list_race_id):
        """Downloads the generated start list file

        :param start_list_race_id: The ID of the start list race to download
        :return: Tuple of (file_path, file_content) if file exists, None otherwise
        """
        try:
            logger.info(f"Attempting to download start list for ID: {start_list_race_id}")
            df = self.app_model.get_start_list_details(start_list_race_id)
            
            if df.empty:
                logger.warning(f"No start list details found for ID: {start_list_race_id}")
                return None
                
            pcm_database_id, pcm_race_id, race_year = df['pcm_database_id'].values[0], df['pcm_race_id'].values[0], df['race_year'].values[0]
            logger.info(f"Found details - database_id: {pcm_database_id}, race_id: {pcm_race_id}, year: {race_year}")
            
            file_path = self.get_start_list_output_file_path(pcm_database_id, pcm_race_id, race_year)
            logger.info(f"Looking for file at: {file_path}")
            
            if not os.path.exists(file_path):
                logger.warning(f"Start list file not found at {file_path}")
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            logger.info(f"Successfully loaded start list file from {file_path}")
            return file_path, file_content
            
        except Exception as e:
            logger.error(f"Error in download_start_list: {str(e)}")
            return None

    def import_pcm_database(self, pcm_version, pcm_database_name):
        """Loads the PCM database into the app instance

        :param pcm_database_name: The name of the PCM database
        :param pcm_version: The version of PCM video game
        """

        self.app_model.import_pcm_data(pcm_version, pcm_database_name)

    def get_pcm_database(self, pcm_database_id):
        """Retrieves PCM databases that have been loaded

        :return:
        """

        df = self.app_model.get_pcm_database(pcm_database_id)
        if df.empty:
            return None
        return df.to_dict(orient='records')[0]

    def get_pcm_databases(self, pcm_version=None):
        """Retrieves PCM databases that have been loaded

        :return:
        """
        df = self.app_model.get_pcm_databases(pcm_version)
        if df.empty:
            return []
        return df.to_dict(orient='records')
    
    def get_race(self, pcm_database_id, pcm_race_id):
        """Retrieves PCM races
        :return:
        """
        df = self.app_model.get_race(pcm_database_id, pcm_race_id)
        logger.info(f"Fetched race with pcm_database_id {pcm_database_id} and pcm_race_id {pcm_race_id}")
        logger.info(df)
        if df.empty:
            return None
        return df.to_dict(orient='records')[0]

    def get_pcm_races(self, pcm_database_id, race_name=None):
        """Retrieves PCM races
        :return:
        """
        df = self.app_model.get_pcm_races(pcm_database_id, race_name=race_name)
        if df.empty:
            return []
        return df.to_dict(orient='records')

    def get_start_lists(self, pcm_database_id, pcm_race_id):
        """Retrieves start lists that have been generated along with the pcm database name

        :return:
        """
        df = self.app_model.get_start_lists(pcm_database_id, pcm_race_id)
        if df.empty:
            return []
        return df.to_dict(orient='records')
