# Test Model API

import unittest
from src.model.model_api import create_model, delete_model_tables, get_start_list_data

class TestModelAPI(unittest.TestCase):

    def setUp(self):
        # Setup code to initialize the database or any required state
        self.database_name = "test_db"

    def tearDown(self):
        # Cleanup code to remove the test database or reset state
        delete_model_tables(['pcm_stg_cyclists', 'pcm_stg_teams', 'pcm_stg_races', 'stg_start_list_cyclists'])

    def test_create_model(self):
        # Test the creation of the model
        create_model()
        # Add assertions to verify the model was created correctly

    def test_get_start_list_data(self):
        # Test fetching start list data
        data = get_start_list_data(self.database_name, "tour de france", 2024)
        # Add assertions to verify the data is as expected

    def test_delete_model_tables(self):
        # Test the deletion of model tables
        delete_model_tables(['pcm_stg_cyclists'])
        # Add assertions to verify the tables were deleted

if __name__ == '__main__':
    unittest.main()