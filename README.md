


# Start List Generator for Pro Cycling Manager

This program generates race start lists for use in single player races by 
pulling real start list data from the internet and generating the PCM start list files for the database of your choosing.

1. Scrapes the web for the requested race start list
2. Extracts the cyclists, teams and races from the PCM database
3. Matches start list to the PCM database and generate a PCM start list XML

## Prerequisites

1. Clone of this repository
2. A PCM Database exported as SQLite to the folder `src/data/pcm_dbs/<database_name>.sqlite`


### Export a PCM Database (.cdb) to a SQLite Database

Download SQLiteExporter.exe
Launch command prompt navigate to the folder where SQLiteExporter.exe is located and export the cdb

    SQLiteExporter.exe -export "Pro Cycling Manager 2024\Cloud\<pcm user name>\Career_1.cdb"
    SQLiteExporter.exe -export "Pro Cycling Manager 2024\Cloud\76561198067930365\Race_5.cdb"

This will generate a .sqlite file in the same PCM folder. Copy or move to the folder `src/data/pcm_dbs` and rename the file to match the `pcm_database_name`

Pro Cycling Manager 2024\Cloud\76561198067930365

## CLI for start list creation
    python ./run.py --pcm_database_name "worlddb_2024" --race_name "Tour de France" --race_year 2024
    python ./run.py --pcm_database_name "worlddb_2024" --race_name "Giro d'Italia" --race_year 2024
    python ./run.py --pcm_database_name "worlddb_2025" --pcm_race_name "Giro d'Italia" --race_name "Giro d'Italia" --race_year 2025
    python ./run.py --pcm_database_name "worlddb_2024" --race_name "vuelta a espana" --pcm_race_name "la vuelta ciclista a españa" --race_year 2024


### Troubleshooting

#### Fetch Start List
    from scrapers import procyclingstats 
    race_year = 2025
    race_name = "tour-de-france"
    scraper = procyclingstats.ProCyclingStatsStartListScraper(race_year, race_name)
    scraper.insert_start_list_raw(fetch_from_web=False)


#### Extract Data from PCM Database

    from src.pcm import pcm_api, extract
    from src.utils import database_helper
    database_name = "worlddb_2024"
    
    pcm_api.load_model(database_name)
    
    extract.get_object(database_name, "team")
    extract.get_object(database_name, "race")
    extract.get_object(database_name, "cyclist")
    extract.get_roster(conn)

Inspect Table Data

from src.model import model_api
from src.utils import database_helper
database_connection = database_helper.get_database_connection(model_api.APP_DATABASE_FILE)

    print(database_helper.run_query(database_connection, "select * from stg_start_list_files"))
    print(database_helper.run_query(database_connection, "select * from stg_start_list_cyclists where race_name like '%giro%'"))
    print(database_helper.run_query(database_connection, "select * from pcm_stg_teams"))
    print(database_helper.run_query(database_connection, "select * from pcm_stg_teams"))
    print(database_helper.run_query(database_connection, "select * from pcm_stg_races"))
    print(database_helper.run_query(database_connection, "select * from pcm_stg_cyclists where cyclist_last_name like '%cepeda%'"))
    print(database_helper.run_query(database_connection, "select team_name, cyclist_first_name || ' ' || cyclist_last_name as cyclist_name from stg_start_list_cyclists where race_name = 'la vuelta ciclista a españa' and race_year = 2024"))

    from src.model import model_api
    df = model_api.get_start_list_data("worlddb_2024", "tour de france", 2024)
    print(df[df['team_name'].str.contains('uno')])

Delete Tables

    from src.model import model_api
    model_api.delete_model_tables(['pcm_stg_cyclists','pcm_stg_teams','pcm_stg_races', 'stg_start_list_cyclists'])
    model_api.delete_model_tables(['stg_start_list_cyclists', 'stg_start_list_files'])


Create Tables

    from src.model import model_api
    model_api.create_model()
    
    from src.utils import database_helper
    conn = database_helper.get_database_connection(model_api.APP_DATABASE_FILE)
    database_helper.list_tables(conn)

### Docker

    docker build -t pcm_startlist .
    docker run -it --rm -v pcm_startlist