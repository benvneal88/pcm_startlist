from time import sleep
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import pandas

from scrapers.scraper_api import StartListScraper
from utils import logger_helper

logger = logger_helper.get_logger(__name__)


def parse_race_index_page(get_race_index_url, class_name):
    logger.info(f"Fetching race data from '{get_race_index_url}'")
    race_index = []
    response = requests.get(get_race_index_url)
    if response.status_code != 200:
        logger.error(f"Failed to retrieve race data from {get_race_index_url}")
        return race_index
    
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "race/" in href:
            race_index.append({"url": href, "name": link.text.strip(), "class": class_name})
    return race_index

def get_race_index() -> List[Dict]:
    """Fetches race name to race url associations to pull start lists from"""
    race_filters = [
        {
            "class": "2.Pro",
            "category": "1",
        },
        {
            "class": "2.UWT",
            "category": "1",
        },
        {
            "class": "2.1",
            "category": "1",
        },
        {
            "class": "2.2",
            "category": "1",
        },
        {
            "class": "2.HC",
            "category": "1",
        },
        {
            "class": "1.Pro",
            "category": "1",
        }  
    ]
    logger.info(f"Fetching race index from Pro Cycling Stats:\n {race_filters}")

    race_index = []
    for race_filter in race_filters:
        sleep(1)  # To avoid hitting the server too fast
        race_index_url = f"https://www.procyclingstats.com/races.php?s=races-database&name=&nation=&class={race_filter.get('class', '')}&category={race_filter.get('category', '')}&year=&season=&month=&filter=Filter"
        logger.info(f"Fetching race index from {race_index_url}")
        race_index.extend(parse_race_index_page(race_index_url, race_filter.get('class', '')))
    return race_index

class ProCyclingStatsStartListScraper(StartListScraper):
    def __init__(self, race_year, race_name, force_start_list_url=None):
        super().__init__(data_source_name="procyclingstats", race_year=race_year, race_name=race_name, force_start_list_url=force_start_list_url)

    def get_start_list_raw_url(self) -> str:
        url = f"https://www.procyclingstats.com/race/{self.race_name}/{self.race_year}/startlist/startlist"
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

        return df

    