
import os
from enum import Enum

APP_PORT = 5000
DATA_PATH = os.path.join(os.getcwd(), "data")
PCM_DATABASE_PATH = os.path.join(DATA_PATH, "dbs", "pcm")
START_LIST_OUTPUT_PATH = os.path.join(DATA_PATH, "output")
START_LIST_INPUT_PATH = os.path.join(DATA_PATH, "input", "startlists")

class PCMTableName(Enum):
    TEAM = "DYN_team"
    RACE = "STA_race"
    CYCLIST = "DYN_cyclist"


PCM_DATABASE_MAPPINGS = {
    "PCM_2025":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        },
    "PCM_2024":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        },
    "PCM_2023":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        }
}

PCM_VERSIONS = list(PCM_DATABASE_MAPPINGS.keys())
