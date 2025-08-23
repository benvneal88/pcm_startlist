
import os
import re
from enum import Enum

APP_PORT = 5000
DATA_PATH = os.path.join(os.getcwd(), "data")
PCM_DATABASE_PATH = os.path.join(DATA_PATH, "dbs", "pcm")
START_LIST_OUTPUT_PATH = os.path.join(DATA_PATH, "output")
START_LIST_INPUT_PATH = os.path.join(DATA_PATH, "input", "startlists")
LOOKUP_PATH = os.path.join(DATA_PATH, "input", "lookups")

class PCMTableName(Enum):
    TEAM = "DYN_team"
    RACE = "STA_race"
    CYCLIST = "DYN_cyclist"


PCM_DATABASE_MAPPINGS = {
    "PCM 2025":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        },
    "PCM 2024":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        },
    "PCM 2023":
        {
            "DYN_team": {"IDteam": "team_id", "gene_sz_shortname": "team_short_name", "gene_sz_name": "team_name"},
            "STA_race": {"IDrace": "race_id", "gene_sz_race_name": "race_name", "gene_sz_abbreviation": "race_abbrreviation", "gene_sz_filename": "file_name"},
            "DYN_cyclist": {"IDcyclist": "cyclist_id", "fkIDteam": "team_id", "gene_sz_lastname": "cyclist_last_name", "gene_sz_firstname": "cyclist_first_name"},
        }
}

PCM_VERSIONS = list(PCM_DATABASE_MAPPINGS.keys())


def get_app_version():
    """Get the application version from setup.py"""
    try:
        # Get the path to the setup.py file (go up from src/utils to root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(current_dir))
        setup_path = os.path.join(root_dir, 'setup.py')
        
        if os.path.exists(setup_path):
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Use regex to find version string
                version_match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
                if version_match:
                    return version_match.group(1)
        
        # Fallback if setup.py is not found or version not found
        return "dev"
    except Exception:
        return "unknown"
