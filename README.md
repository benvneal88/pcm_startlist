# pcm_start_list


python3 -m pip install -e .

create start list for pcm


Export a Pro Cycling Manager database (.cdb) to a SQLite Database

Fetch the startlist from a website with a supported scraper

from scrapers import procyclingstats 
year = 2024
race_name = "tour-de-france"
scraper = procyclingstats.ProCyclingStatsStartListScraper(year, race_name)
scraper.sync_start_list_to_database()

### Maintenance

Delete Tables

Create Tables

    from model import api
    api.create_model()

### Docker

    docker build -t pcm_startlist .
    docker run -it --rm -v pcm_startlist