import datetime
import os

import requests
from bs4 import BeautifulSoup
import pandas as pd

from model import api as model_api

from utils import logger
logger = logger.get_logger_init()


def download_start_list(url: str, save_file_path):
    logger.info(f"Fetching start list from url: {url} and saving to {save_file_path}")
    response = requests.get(url)

    logger.info(f"successfully retrieved data {response.status_code}")
    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response.text)

    logger.info(f"saved data to file {save_file_path}")


def pcs_transform(html_string) -> pd.DataFrame:
    #logger.info(f"Parsing start_list file {html_file_path}")

    # with open(html_file_path, "r", encoding="utf-8") as _file:
    #     soup = BeautifulSoup(str(_file.read()), 'html.parser')

    soup = BeautifulSoup(html_string, "html.parser")

    team_dict = {}
    #for _team_tag in soup.find_all("li", class_='team'):
    for _team_tag in soup.find_all("li"):
        team_soup = BeautifulSoup(str(_team_tag), 'html.parser')
        team_attribute_tags = team_soup.find_all("a")

        _team_name = ""

        # loop through team attributes which include the team name and all rider names
        for team_attribute in team_attribute_tags:

            _attribute_id = team_attribute.get("href")
            _attribute_name = team_attribute.string
            #print(_attribute_id)

            if "team/" in _attribute_id:
                #print(f"Found new team: {_attribute_id}")
                _team_name = _attribute_id.replace("team/", "")
                _team_name = _team_name.replace("-", " ")

            elif "rider/" in _attribute_id:
                # append rider to team dictionary
                cyclist_name = _attribute_id.replace("rider/", "")
                cyclist_name = cyclist_name.replace("-", " ")
                rider_set = (_attribute_name, cyclist_name)

                if _team_name not in team_dict.keys():
                    #print(f"\t adding rider to new team: {_attribute_id}")
                    team_dict[_team_name] = [rider_set]
                else:
                    #print(f"\t adding rider to existing team: {_attribute_id}")
                    old_rider_list = team_dict[_team_name]
                    old_rider_list.append(rider_set)
                    team_dict[_team_name] = old_rider_list
                    #print(old_rider_list)

    normalized_rider_list = []

    for _team_name, _rider_list in team_dict.items():
        logger.debug(_team_name)
        for _rider in _rider_list:
            _set = (_team_name, _rider)
            normalized_rider_list.append(_set)

    normalized_team_list = [_set[0] for _set in normalized_rider_list]
    normalized_rider_name_list = [_set[1][0] for _set in normalized_rider_list]
    normalized_rider_name_id_list = [_set[1][1] for _set in normalized_rider_list]

    normalized_dict = {"team_name": normalized_team_list, "rider_name": normalized_rider_name_list, "cyclist_name": normalized_rider_name_id_list}

    df = pd.DataFrame.from_dict(normalized_dict)

    # remove any extra rider names picked up without teams
    df = df[df['team_name'] != '']
    df["team_name"] = df["team_name"].str.replace(" \d+", "", regex=True)
    df["cyclist_last_name"] = df["rider_name"].apply(lambda x: ' '.join(word for word in x.split() if word.isupper())).str.lower()
    df["cyclist_first_name"] = df["rider_name"].apply(lambda x: ' '.join(word for word in x.split() if not word.isupper())).str.lower()
    df = df.drop(columns=["rider_name"])

    return df


def save_start_list(data_source, year, race_name, url, file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()

    row_dict = {
        "data_source": [data_source],
        "year": [year],
        "race_name": [race_name],
        "url": [url],
        "blob_content": [file_bytes],
        "downloaded_at": [datetime.datetime.utcnow().isoformat()]
    }

    df = pd.DataFrame.from_dict(row_dict)
    model_api.insert_start_list_files(df)


def get_start_list(data_source, year, race_name, file_path, force_refresh=False):
    url = f"https://www.procyclingstats.com/race/{race_name}/{year}/startlist/startlist"

    if not os.path.exists(file_path) or force_refresh:
        download_start_list(url, file_path)
        save_start_list(data_source, year, race_name, url, file_path)

    start_list_df = None
    if data_source == "pcs":
        html_string = model_api.fetch_start_list(data_source, year, race_name)
        start_list_df = pcs_transform(html_string)
        start_list_df["year"] = year
        start_list_df["race_name"] = race_name


    print(f"Teams: {start_list_df['team_name'].unique()}")
    print(f"Unique Riders: {len(start_list_df['cyclist_name'].unique())}")
    return start_list_df


if __name__ == "__main__":

    data_source = "pcs"
    race_name = "tour-de-france"
    year = "2023"

    file_name = f"{race_name}-{year}.html"
    file_path = os.path.join("data", "start_lists", "pcs", file_name)

    # df = get_start_list(
    #     data_source=data_source,
    #     race_name=race_name,
    #     year=year,
    #     file_path=file_path,
    # )
    #print(model_api.run_query("select * from stg_start_list_cyclists"))

    #model_api.insert_start_list_cyclists(df)

    #print(df.head(100))
    #df.to_csv("data/start_list.csv")





