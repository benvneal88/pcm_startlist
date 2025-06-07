# Test for Scrapers

import unittest
from src.scrapers.procyclingstats import ProCyclingStatsStartListScraper

class TestProCyclingStatsScraper(unittest.TestCase):

    def setUp(self):
        self.race_year = 2025
        self.race_name = "tour-de-france"
        self.scraper = ProCyclingStatsStartListScraper(self.race_year, self.race_name)

    def test_scraper_initialization(self):
        self.assertIsInstance(self.scraper, ProCyclingStatsStartListScraper)

    def test_fetch_start_list_raw(self):
        # Assuming fetch_from_web=True will fetch data from the web
        result = self.scraper.insert_start_list_raw(fetch_from_web=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)  # Assuming the result is a list of start list data

    def test_insert_start_list_raw(self):
        # Test the insertion of raw start list data
        raw_data = [{"cyclist": "John Doe", "team": "Team A", "race": "Tour de France"}]
        result = self.scraper.insert_start_list_raw(raw_data)
        self.assertTrue(result)  # Assuming the method returns True on successful insertion

    def tearDown(self):
        # Clean up any resources if necessary
        pass

if __name__ == '__main__':
    unittest.main()