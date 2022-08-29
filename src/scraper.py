import os
import sys

import datetime

import requests
from bs4 import BeautifulSoup
import pandas
import re


url = "https://www.procyclingstats.com/race/vuelta-a-espana/2022/stage-9/startlist"
url = "https://tabs.ultimate-guitar.com/b/beck/golden_age_crd.htm"
root_directory = os.path.join(os.getcwd(), "src", "data")

def get_start_list(url: str, save_file_path):
    print(f"Fetching start list from ur: {url} and saving to {save_file_path}")
    response = requests.get(url)

    print(f"successfully retrieved data from: {response.status_code}")


    with open(save_file_path, "w", encoding="utf-8") as _file:
        _file.write(response.text)

    print(f"saved data to file {save_file_path}")


def transform_html_to_df(file_path):

    with open(file_path, "r", encoding="utf-8") as _file:
        soup = BeautifulSoup(str(_file.read()), 'html.parser')

    team_dict = {}
    for _team_tag in soup.find_all("li", class_='team'):

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
        for _rider in _rider_list:
            _set = (_team_id, _rider)
            normalized_rider_list.append(_set)

    normalized_team_list = [_set[0] for _set in normalized_rider_list]
    normalized_rider_name_list = [_set[1][0] for _set in normalized_rider_list]
    normalized_rider_name_id_list = [_set[1][1] for _set in normalized_rider_list]

    normalized_dict = {"team_id": normalized_team_list, "rider_name": normalized_rider_name_list, "rider_id": normalized_rider_name_id_list}

    team_df = pandas.DataFrame.from_dict(normalized_dict)
    return team_df



if __name__ == "__main__":
    file_path = os.path.join(root_directory, f"start_list.html")

    # get_start_list(
    #     url=url,
    #     save_file_path=file_path
    # )

    team_df = transform_html_to_df(file_path=file_path)
    print(team_df)



