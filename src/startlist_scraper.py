import os
import re
import numpy
import requests
from bs4 import BeautifulSoup
import pandas as pd

import utils

logger = utils.get_logger()


DATA_DIRECTORY = "data"

def get_start_list(url: str, save_file_path):
    """Fetches start list html from url and saves the html as a file locally"""
    logger.info(f"Fetching start list from url: {url} and saving to {save_file_path}")
    response = requests.get(url)

    logger.info(f"successfully retrieved data {response.status_code}")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response.text)

    logger.info(f"saved data to file {save_file_path}")


def transform_html_to_startlist(html_file_path) -> pd.DataFrame:
    """Parses start list html into a dataframe"""

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
    df = team_df[team_df['team_id'] != '']

    def extract_year_and_remove(text):
        match = re.search(r'\b(\d{4})\b', text)
        if match:
            year = int(match.group())
            text_without_year = re.sub(r'\b\d{4}\b', '', text)
            return year, text_without_year.strip()
        else:
            return None, text

    df['year'], df['team_id'] = zip(*df['team_id'].map(extract_year_and_remove))
    df.rename(columns={'team_id': 'team_name'})
    df = df.drop(columns=['rider_name'])
    df = df.rename(columns={'rider_id': 'rider_name'})
    return df


def get_startlist(year, race_name, force_refresh=False):
    url = f"https://www.procyclingstats.com/race/{race_name}/{year}/startlist/startlist"
    file_name = f"startlist_{race_name}_{year}.html"

    file_path = os.path.join(DATA_DIRECTORY, file_name)

    if not os.path.exists(file_path) or force_refresh:
        get_start_list(url, file_path)
    
    startlist_df = transform_html_to_startlist(html_file_path=file_path)
    return startlist_df


if __name__ == "__main__":

    race_name = "giro-d-italia"
    year = "2024"

    # race_name = "tour-de-france"
    # year = "2023"

    df = get_startlist(year, race_name)

    print(f"Riders: {df['rider_name']}")
    print(f"Teams: {df['team_id'].unique()}")
    print(f"Unique Riders: {len(df['rider_name'].unique())}")
    import pdb; pdb.set_trace()
    #print(df.head(100))
    #df.to_csv("data/startlist.csv")





