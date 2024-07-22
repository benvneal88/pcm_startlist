from typing import List, Dict
import requests
from src.scrapers.scraper_api import StartListScraper
from bs4 import BeautifulSoup
import pandas
from src.utils import logger_helper
logger = logger_helper.get_logger(__name__)


class ProCyclingStatsStartListScraper(StartListScraper):
    def __init__(self, race_year, race_name):
        super().__init__(race_year=race_year, race_name=race_name, data_source_name="procyclingstats")

    def get_start_list_raw_url(self) -> str:
        url = f"https://www.procyclingstats.com/race/{self.race_name_dashed}/{self.race_year}/startlist/startlist"
        return url

    def transform_raw_start_list(self, html_string) -> List[Dict]:
        # logger.info(f"Parsing start_list file {html_file_path}")

        # with open(html_file_path, "r", encoding="utf-8") as _file:
        #     soup = BeautifulSoup(str(_file.read()), 'html.parser')

        soup = BeautifulSoup(html_string, "html.parser")

        team_dict = {}
        # for _team_tag in soup.find_all("li", class_='team'):
        for _team_tag in soup.find_all("li"):
            team_soup = BeautifulSoup(str(_team_tag), 'html.parser')
            team_attribute_tags = team_soup.find_all("a")

            _team_name = ""

            # loop through team attributes which include the team name and all rider names
            for team_attribute in team_attribute_tags:

                _attribute_id = team_attribute.get("href")
                _attribute_name = team_attribute.string
                # print(_attribute_id)

                if "team/" in _attribute_id:
                    # print(f"Found new team: {_attribute_id}")
                    _team_name = _attribute_id.replace("team/", "")
                    _team_name = _team_name.replace("-", " ")

                elif "rider/" in _attribute_id:
                    # append rider to team dictionary
                    cyclist_name = _attribute_id.replace("rider/", "")
                    cyclist_name = cyclist_name.replace("-", " ")
                    rider_set = (_attribute_name, cyclist_name)

                    if _team_name not in team_dict.keys():
                        # print(f"\t adding rider to new team: {_attribute_id}")
                        team_dict[_team_name] = [rider_set]
                    else:
                        # print(f"\t adding rider to existing team: {_attribute_id}")
                        old_rider_list = team_dict[_team_name]
                        old_rider_list.append(rider_set)
                        team_dict[_team_name] = old_rider_list
                        # print(old_rider_list)

        normalized_rider_list = []

        for _team_name, _rider_list in team_dict.items():
            logger.debug(_team_name)
            for _rider in _rider_list:
                _set = (_team_name, _rider)
                normalized_rider_list.append(_set)

        normalized_team_list = [_set[0] for _set in normalized_rider_list]
        normalized_rider_name_list = [_set[1][0] for _set in normalized_rider_list]
        normalized_rider_name_id_list = [_set[1][1] for _set in normalized_rider_list]

        normalized_dict = {"team_name": normalized_team_list, "rider_name": normalized_rider_name_list,
                           "cyclist_name": normalized_rider_name_id_list}

        df = pandas.DataFrame.from_dict(normalized_dict)

        # remove any extra rider names picked up without teams
        df = df[df['team_name'] != '']
        df["team_name"] = df["team_name"].str.replace(" \d+", "", regex=True)
        df["cyclist_last_name"] = df["rider_name"].apply(
            lambda x: ' '.join(word for word in x.split() if word.isupper())).str.lower()
        df["cyclist_first_name"] = df["rider_name"].apply(
            lambda x: ' '.join(word for word in x.split() if not word.isupper())).str.lower()
        df = df.drop(columns=["rider_name"])
        df["race_year"] = self.race_year
        df["race_name"] = self.race_name

        return df


    def transform_raw_start_list_races(self, html_string):
        soup = BeautifulSoup(html_string, "html.parser")
