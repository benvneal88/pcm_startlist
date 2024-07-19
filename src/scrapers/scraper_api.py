import sys

import requests
import datetime
import os

import pandas
from abc import ABC, abstractmethod
import sqlite3
from typing import List, Dict

from src.model import model_api
from src.utils import logger_helper
logger = logger_helper.get_logger(__name__)


def download_file(url: str, save_file_path):
    logger.info(f"Fetching start list from url: {url} and saving to {save_file_path}")
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

    logger.info(f"successfully retrieved data {response.status_code}")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write()

    logger.info(f"saved data to file {save_file_path}")


def insert_start_list_file_data_to_database(data_source, race_year, race_name, url, file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    logger.info(f"Inserting into table '{race_year}' - '{race_name}' - '{url}' - '{data_source}'")
    row_dict = {
        "data_source": [data_source],
        "race_year": [race_year],
        "race_name": [race_name],
        "url": [url],
        "blob_content": [file_bytes.decode('utf-8')],
    }

    df = pandas.DataFrame.from_dict(row_dict)
    model_api.insert_start_list_files(df)


class StartListScraper(ABC):
    def __init__(self, race_year: int, race_name: str, data_source_name: str):
        self.race_year = race_year
        self.race_name = race_name.replace("'", " ")
        self.race_name_dashed = self.race_name.replace(" ", "-")
        self.start_list_url = self.get_start_list_raw_url()
        self.data_source_name = data_source_name

    @abstractmethod
    def get_start_list_raw_url(self) -> str:
        pass

    def get_start_list_raw_dir_path(self) -> str:
        return os.path.join(os.getcwd(), "src", "data", "source_start_lists")

    def get_start_list_raw_file_name(self) -> str:
        return f"{self.data_source_name}-{self.race_name_dashed}-{self.race_year}.html"

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

    def get_start_list_raw(self, refresh: bool = False) -> bytes:
        """"Fetches Start List raw html data"""
        start_list_raw_file_path = self.get_start_list_raw_file_path()
        if not os.path.exists(self.get_start_list_raw_dir_path()):
            os.makedirs(self.get_start_list_raw_dir_path())
        if refresh:
            download_file(self.start_list_url, start_list_raw_file_path)

        with open(start_list_raw_file_path, "rb") as f:
            raw_text = f.read()

        return raw_text

    def sync_start_list_to_database(self, refresh=False):
        raw_file_exists = self.does_start_list_raw_file_exist()
        if refresh or not raw_file_exists:
            logger.info(f"Fetching latest start list from: '{self.start_list_url}'")
            self.get_start_list_raw(refresh=True)
        elif not self.does_start_list_raw_file_exist():
            logger.info(f"Start list doesn't exist, fetching latest start list from: '{self.start_list_url}'")
            self.get_start_list_raw(refresh=True)
        else:
            logger.info(f"Existing start list exists: '{self.get_start_list_raw_file_path()}'")

        logger.info(f"Inserting raw html data into the database: '{self.start_list_url}'")
        insert_start_list_file_data_to_database(
            data_source=self.data_source_name,
            race_year=self.race_year,
            race_name=self.race_name,
            url=self.start_list_url,
            file_path=self.get_start_list_raw_file_path()
        )

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
            return False

        model_api.insert_start_list_riders(df, self.race_name, self.race_year)
        return True