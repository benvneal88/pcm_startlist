import unittest
from src.pcm import pcm_api, extract
from src.utils import database_helper

class TestPCMDatabase(unittest.TestCase):

    def setUp(self):
        self.database_name = "worlddb_2024"
        self.conn = database_helper.get_database_connection(pcm_api.APP_DATABASE_FILE)
        pcm_api.load_model(self.database_name)

    def tearDown(self):
        database_helper.close_connection(self.conn)

    def test_extract_teams(self):
        teams = extract.get_object(self.database_name, "team")
        self.assertIsInstance(teams, list)
        self.assertGreater(len(teams), 0)

    def test_extract_races(self):
        races = extract.get_object(self.database_name, "race")
        self.assertIsInstance(races, list)
        self.assertGreater(len(races), 0)

    def test_extract_cyclists(self):
        cyclists = extract.get_object(self.database_name, "cyclist")
        self.assertIsInstance(cyclists, list)
        self.assertGreater(len(cyclists), 0)

    def test_roster_data(self):
        roster = extract.get_roster(self.conn)
        self.assertIsInstance(roster, list)
        self.assertGreater(len(roster), 0)

if __name__ == '__main__':
    unittest.main()