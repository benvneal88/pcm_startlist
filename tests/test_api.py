import unittest
from unittest.mock import MagicMock, patch

from src import api

class TestApi(unittest.TestCase):
    @patch("src.api.pcm_api.PCMDatabase")
    @patch("src.api.model_api")
    def test_load_pcm_db(self, mock_model_api, mock_PCMDatabase):
        # Arrange
        mock_app = MagicMock()
        mock_pcm_db = MagicMock()
        mock_PCMDatabase.return_value = mock_pcm_db
        mock_model_api.check_for_pcm_data.return_value = False
        mock_pcm_db.get_pcm_object.return_value = "df"
        pcm_objects = [MagicMock(value="team"), MagicMock(value="race")]
        with patch("src.api.pcm_api.ObjectName", pcm_objects):
            # Act
            api.load_pcm_db(mock_app, "test_db", "2024")

        # Assert
        mock_PCMDatabase.assert_called_once_with("test_db", "2024")
        mock_model_api.check_for_pcm_data.assert_called_once_with("test_db")
        self.assertEqual(mock_pcm_db.get_pcm_object.call_count, len(pcm_objects))
        self.assertEqual(mock_app.insert_pcm_object.call_count, len(pcm_objects))

if __name__ == "__main__":
    unittest.main()