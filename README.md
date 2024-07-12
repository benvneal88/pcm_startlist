# pcm_start_list


python3 -m pip install -e .

create start list for pcm


Export a Pro Cycling Manager database (.cdb) to a SQLite Database

Download SQLiteExporter.exe
Launch command prompt and type in the following command to export a PCM .cdb database
`SQLiteExporter.exe -export "Pro Cycling Manager 2024\Cloud\<pcm user name>\Career_1.cdb"`



### Fetch Start List
    from scrapers import procyclingstats 
    year = 2024
    race_name = "tour-de-france"
    scraper = procyclingstats.ProCyclingStatsStartListScraper(year, race_name)
    scraper.sync_start_list_to_database(refresh=False)

### Maintenance

Extract Data from PCM Database

    from pcm import pcm_api
    database_name = "worlddb_2024.sqlite"
    pcm_api.load_model(database_name)

    from utils import database_helper
    conn = pcm_api.get_database_file(database_name)
    database_helper.get_metadata(conn, "STA_race")

Inspect Table Data

    from model import model_api
    model_api.list_tables()
    print(model_api.run_query("select * from stg_start_list_files"))

Delete Tables

    from model import model_api
    model_api.drop_all_tables()

Create Tables

    from model import model_api
    model_api.create_model()
    model_api.list_tables()

### Docker

    docker build -t pcm_startlist .
    docker run -it --rm -v pcm_startlist