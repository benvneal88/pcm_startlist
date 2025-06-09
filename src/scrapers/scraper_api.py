import sys

import requests
import datetime
import os

import pandas
from abc import ABC, abstractmethod
import sqlite3
from typing import List, Dict
from model import model_api
from utils import logger_helper
logger = logger_helper.get_logger(__name__)

STARTLIST_DIR_PATH = os.path.join("src", "data", "startlists")


def download_file(url: str, save_file_path):
    logger.info(f"Fetching start list from url: '{url}' and saving to {save_file_path}")
    response = requests.get(url)
    try:
        response.raise_for_status()
    except Exception as e:
        logger.exception(e)
        logger.error(f"Failed to get successful response from url '{url}'")
        logger.info(f"Exiting program")
        sys.exit(1)

    response_text = response.text
    if "Page not found" in response_text:
        logger.error(f"Page not found! '{url}'")
        sys.exit(1)

    logger.info(f"Successfully downloaded data from url '{url}'")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response_text)

    logger.info(f"saved data to file {save_file_path}")


class StartListScraper(ABC):
    def __init__(self, race_year: int, race_name: str):
        self.race_year = race_year
        self.race_name = race_name.replace("'", " ")
        self.race_name_dashed = self.race_name.replace(" ", "-")
        self.start_list_url = self.get_start_list_raw_url()
        self.data_source_name = "unknown"

    @abstractmethod
    def get_start_list_raw_url(self) -> str:
        pass

    def get_start_list_raw_dir_path(self) -> str:
        return STARTLIST_DIR_PATH

    def get_start_list_raw_file_name(self) -> str:
        return f"{self.data_source_name}-{self.race_name_dashed}-{self.race_year}.html"

    def get_start_list_raw_file_path(self) -> str:
        return os.path.join(self.get_start_list_raw_dir_path(), self.data_source_name, self.get_start_list_raw_file_name())

    def does_start_list_raw_file_exist(self):
        if os.path.exists(self.get_start_list_raw_file_path()):
            return True
        else:
            return False

    @abstractmethod
    def transform_raw_start_list(self, html_string) -> List[Dict]:
        pass

    @abstractmethod
    def transform_raw_start_list_races(self, html_string) -> List[Dict]:
        pass

    def get_start_list_raw(self, refresh: bool = False) -> bytes:
        """"Fetches Start List raw html data"""
        start_list_raw_file_path = self.get_start_list_raw_file_path()
        if not os.path.exists(self.get_start_list_raw_dir_path()):
            os.makedirs(self.get_start_list_raw_dir_path())
        if refresh:
            download_file(self.start_list_url, start_list_raw_file_path)
    
        return start_list_raw_file_path

    def fetch_start_list(self, fetch_from_web=False):
        """Fetches the start list for a specific race."""
        raw_file_exists = self.does_start_list_raw_file_exist()
        if fetch_from_web or not raw_file_exists:
            start_list_raw_file_path = self.get_start_list_raw(refresh=True)
        else:
            start_list_raw_file_path = self.get_start_list_raw(refresh=False)

        return self.start_list_url, start_list_raw_file_path

    def insert_start_list_cyclists(self):
        html_string = model_api.get_start_list_raw_html(
            self.data_source_name,
            self.race_year,
            self.race_name
        )

        try:
            df = self.transform_raw_start_list(html_string)
        except Exception as e:
            logger.exception(e)
            logger.error("Failed to transform the html into a start list dataframe")
            sys.exit(1)

        model_api.insert_start_list_riders(df, self.race_name, self.race_year)

    def insert_start_list_races(self):
        html_string = model_api.get_race_list_races_raw_html(
            self.data_source_name,
            self.race_year
        )

        try:
            df = self.transform_raw_start_list_races(html_string)
        except Exception as e:
            logger.exception(e)
            logger.error("Failed to transform the html into a start list dataframe")
            sys.exit(1)

        model_api.insert_start_list_riders(df, self.race_name, self.race_year)