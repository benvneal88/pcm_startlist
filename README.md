# pcm_start_list


python3 -m pip install -e .

create start list for pcm


Export a Pro Cycling Manager database (.cdb) to a SQLite Database

Download SQLiteExporter.exe
Launch command prompt and type in the following command to export a PCM .cdb database
`SQLiteExporter.exe -export "Pro Cycling Manager 2024\Cloud\<pcm user name>\Career_1.cdb"`


###
    cd src
    python ./run.py --pcm_database_name "worlddb_2024" --race_name "Tour de France" --year 2024

### Fetch Start List
    from scrapers import procyclingstats 
    year = 2024
    race_name = "tour-de-france"
    scraper = procyclingstats.ProCyclingStatsStartListScraper(year, race_name)
    scraper.sync_start_list_to_database(refresh=False)


### Maintenance

Extract Data from PCM Database

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
    database_connection = database_helper.get_database_connection(model_api.APP_DATABASE_FILE_NAME)
    print(database_helper.run_query(database_connection, "select * from stg_start_list_files"))
    print(database_helper.run_query(database_connection, "select * from pcm_stg_teams"))
    print(database_helper.run_query(database_connection, "select * from pcm_stg_races"))

Delete Tables

    from src.model import model_api
    model_api.delete_model_tables(['pcm_stg_cyclists','pcm_stg_teams','pcm_stg_races'])

Create Tables

    from src.model import model_api
    model_api.create_model()
    
    from src.utils import database_helper
    conn = database_helper.get_database_connection(model_api.APP_DATABASE_FILE)
    database_helper.list_tables(conn)

### Docker

    docker build -t pcm_startlist .
    docker run -it --rm -v pcm_startlist