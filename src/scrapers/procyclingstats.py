# File: /pcm_startlist/pcm_startlist/src/scrapers/procyclingstats.py

import requests
from bs4 import BeautifulSoup

class ProCyclingStatsStartListScraper:
    def __init__(self, race_year, race_name):
        self.race_year = race_year
        self.race_name = race_name
        self.base_url = f"https://www.procyclingstats.com/race/{race_name}/{race_year}/startlist"

    def fetch_start_list(self):
        response = requests.get(self.base_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from {self.base_url}")
        return response.text

    def parse_start_list(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        start_list = []
        # Assuming the start list is in a specific table structure
        table = soup.find('table', class_='startlist')
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            cyclist = {
                'name': cols[1].text.strip(),
                'team': cols[2].text.strip(),
                'number': cols[0].text.strip()
            }
            start_list.append(cyclist)
        return start_list

    def insert_start_list_raw(self, fetch_from_web=True):
        if fetch_from_web:
            html = self.fetch_start_list()
            start_list = self.parse_start_list(html)
            # Here you would insert the start_list into your database
            # This is a placeholder for the actual database insertion logic
            print(start_list)  # Replace with actual database insertion
        else:
            print("Fetching from web is disabled.")