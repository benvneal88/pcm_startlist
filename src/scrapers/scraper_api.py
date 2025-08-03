import sys
import requests
import datetime
import os
import pandas
from abc import ABC, abstractmethod
import sqlite3
from typing import List, Dict

from model import model_api
from utils import logger_helper, commons

logger = logger_helper.get_logger(__name__)




def download_file(url: str, save_file_path):
    logger.info(f"Fetching start list from url: '{url}' and saving to {save_file_path}")
    response = requests.get(url)
    try:
        response.raise_for_status()
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to get successful response from url '{url}'")
        return False

    response_text = response.text
    if "Page not found" in response_text:
        logger.error(f"Page not found! '{url}'")
        return False

    logger.info(f"Successfully downloaded data from url '{url}'")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response_text)

    logger.info(f"saved data to file {save_file_path}")
    return True

class StartListScraper(ABC):
    def __init__(self, data_source_name, race_year: int = None, race_name: str = None, force_start_list_url: str = None):
        self.race_year = race_year
        self.race_name = race_name
        if (not self.race_name or not self.race_year) and not force_start_list_url:
            logger.error("You must provide either race_name and race_year or force_start_list_url to the StartListScraper")
            sys.exit(1)

        self.start_list_url = force_start_list_url if force_start_list_url else self.get_start_list_raw_url()
        self.data_source_name = data_source_name


    @abstractmethod
    def get_start_list_raw_url(self) -> str:
        pass

    def get_start_list_raw_dir_path(self) -> str:
        start_list_raw_path = os.path.join(commons.START_LIST_INPUT_PATH, self.data_source_name)
        os.makedirs(start_list_raw_path, exist_ok=True)
        return start_list_raw_path

    def get_start_list_raw_file_name(self) -> str:
        if self.race_name and self.race_year:
            return f"{self.race_name}-{self.race_year}.html"
        return f"{self.start_list_url.replace('/', '_').replace(':', '_')}.html"

    def get_start_list_raw_file_path(self) -> str: 
        return os.path.join(self.get_start_list_raw_dir_path(), self.get_start_list_raw_file_name())

    def does_start_list_raw_file_exist(self):
        if os.path.exists(self.get_start_list_raw_file_path()):
            return True
        else:
            return False

    @abstractmethod
    def transform_raw_start_list(self, html_string) -> List[Dict]:
        pass

    def get_start_list_raw(self, start_list_raw_file_path) -> bytes:
        """"Fetches Start List raw html data"""
        if not os.path.exists(self.get_start_list_raw_dir_path()):
            os.makedirs(self.get_start_list_raw_dir_path())
        exit_code = download_file(self.start_list_url, start_list_raw_file_path)
        return exit_code

    def fetch_start_list(self):
        """Fetches the start list for a specific race."""
        raw_file_exists = self.does_start_list_raw_file_exist()
        start_list_raw_file_path = self.get_start_list_raw_file_path()
        is_success = self.get_start_list_raw(start_list_raw_file_path)

        return self.start_list_url, start_list_raw_file_path, is_success

    @abstractmethod
    def get_race_index(self) -> List[Dict]:
        pass
