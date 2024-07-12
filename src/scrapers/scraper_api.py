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


def download_file(url: str, save_file_path):
    logger.info(f"Fetching start list from url: {url} and saving to {save_file_path}")
    response = requests.get(url)

    logger.info(f"successfully retrieved data {response.status_code}")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response.text)

    logger.info(f"saved data to file {save_file_path}")


def insert_start_list_file_data_to_database(data_source, year, race_name, url, file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    logger.info(f"Inserting into table '{year}' - '{race_name}' - '{url}' - '{data_source}'")
    row_dict = {
        "data_source": [data_source],
        "year": [year],
        "race_name": [race_name],
        "url": [url],
        "blob_content": [file_bytes.decode('utf-8')],

    }

    df = pandas.DataFrame.from_dict(row_dict)
    import pdb; pdb.set_trace()
    model_api.insert_start_list_files(df)


class StartListScraper(ABC):
    def __init__(self, year: int, race_name: int, data_source_name: str):
        self.year = year
        self.race_name = race_name
        self.start_list_url = self.get_start_list_raw_url()
        self.data_source_name = data_source_name

    @abstractmethod
    def get_start_list_raw_url(self) -> str:
        pass

    def get_start_list_raw_dir_path(self) -> str:
        return os.path.join("data", "start_lists")

    def get_start_list_raw_file_name(self) -> str:
        return f"{self.data_source_name}-{self.race_name}-{self.year}.html"

    def get_start_list_raw_file_path(self) -> str:
        return os.path.join(self.get_start_list_raw_dir_path(), self.get_start_list_raw_file_name())

    @abstractmethod
    def transform_raw_start_list(self, html_string) -> List[Dict]:
        pass

    def get_start_list_raw(self, refresh: bool = False) -> str:
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
        if refresh:
            self.get_start_list_raw(refresh=True)
            logger.info(f"Inserting raw html data into the database: '{self.start_list_url}'")
        insert_start_list_file_data_to_database(
            data_source=self.data_source_name,
            year=self.year,
            race_name=self.race_name,
            url=self.start_list_url,
            file_path=self.get_start_list_raw_file_path()
        )

        logger.info(f"Fetching raw html data from the database")
        html_string = model_api.get_start_list_raw_html(
            self.data_source_name,
            self.year,
            self.race_name
        )
        df = self.transform_raw_start_list(html_string)

        print(f"Teams: {df['team_name'].unique()}")
        print(f"Unique Riders: {len(df['cyclist_name'].unique())}")
        return df