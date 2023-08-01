import os

import numpy
import requests
from bs4 import BeautifulSoup
import pandas as pd

import utils

logger = utils.get_logger_init()




def get_start_list(url: str, save_file_path):
    logger.info(f"Fetching start list from ur: {url} and saving to {save_file_path}")
    response = requests.get(url)

    logger.info(f"successfully retrieved data {response.status_code}")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response.text)

    logger.info(f"saved data to file {save_file_path}")


def transform_html_to_startlist(html_file_path) -> pd.DataFrame:
    logger.info(f"Parsing start list file {html_file_path}")

    with open(html_file_path, "r", encoding="utf-8") as _file:
        soup = BeautifulSoup(str(_file.read()), 'html.parser')

    team_dict = {}
    #for _team_tag in soup.find_all("li", class_='team'):
    for _team_tag in soup.find_all("li"):
        team_soup = BeautifulSoup(str(_team_tag), 'html.parser')
        team_attribute_tags = team_soup.find_all("a")

        _team_id = ""

        # loop through team attributes which include the team name and all rider names
        for team_attribute in team_attribute_tags:

            _attribute_id = team_attribute.get("href")
            _attribute_name = team_attribute.string
            #print(_attribute_id)

            if "team/" in _attribute_id:
                #print(f"Found new team: {_attribute_id}")
                _team_id = _attribute_id.replace("team/", "")
                _team_id = _team_id.replace("-", " ")

            elif "rider/" in _attribute_id:
                # append rider to team dictionary
                rider_id = _attribute_id.replace("rider/", "")
                rider_id = rider_id.replace("-", " ")
                rider_set = (_attribute_name, rider_id)

                if _team_id not in team_dict.keys():
                    #print(f"\t adding rider to new team: {_attribute_id}")
                    team_dict[_team_id] = [rider_set]
                else:
                    #print(f"\t adding rider to existing team: {_attribute_id}")
                    old_rider_list = team_dict[_team_id]
                    old_rider_list.append(rider_set)
                    team_dict[_team_id] = old_rider_list
                    #print(old_rider_list)

    normalized_rider_list = []

    for _team_id, _rider_list in team_dict.items():
        logger.debug(_team_id)
        for _rider in _rider_list:
            _set = (_team_id, _rider)
            normalized_rider_list.append(_set)

    normalized_team_list = [_set[0] for _set in normalized_rider_list]
    normalized_rider_name_list = [_set[1][0] for _set in normalized_rider_list]
    normalized_rider_name_id_list = [_set[1][1] for _set in normalized_rider_list]

    normalized_dict = {"team_id": normalized_team_list, "rider_name": normalized_rider_name_list, "rider_id": normalized_rider_name_id_list}

    team_df = pd.DataFrame.from_dict(normalized_dict)

    # remove any extra rider names picked up without teams
    team_df = team_df[team_df['team_id'] != '']
    return team_df


def get_startlist_from_url(url, file_name, force_refresh=False):
    file_path = os.path.join(DATA_DIRECTORY, file_name)

    if not os.path.exists(file_path) or force_refresh:
        get_start_list(url, file_path)

    startlist_df = transform_html_to_startlist(html_file_path=file_path)
    return startlist_df


if __name__ == "__main__":

    url = "https://www.procyclingstats.com/race/tour-de-france/2023/startlist/startlist"
    file_path = os.path.join("pcm_dbs")

    file_name = "startlist_tdf_2023.html"

    df = get_startlist_from_url(url, file_name)

    print(f"Teams: {df['team_id'].unique()}")
    print(f"Unique Riders: {len(df['rider_id'].unique())}")
    #print(df.head(100))
    #df.to_csv("data/startlist.csv")





