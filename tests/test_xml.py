# Test XML Generation Functionality

import unittest
from src.xml.generator import generate_start_list_xml

class TestXMLGeneration(unittest.TestCase):

    def setUp(self):
        # Setup any necessary data or state before each test
        self.race_data = {
            'race_name': 'Tour de France',
            'race_year': 2024,
            'cyclists': [
                {'name': 'John Doe', 'team': 'Team A'},
                {'name': 'Jane Smith', 'team': 'Team B'},
            ]
        }
        self.expected_xml_structure = """<start_list>
    <race name="Tour de France" year="2024">
        <cyclist>
            <name>John Doe</name>
            <team>Team A</team>
        </cyclist>
        <cyclist>
            <name>Jane Smith</name>
            <team>Team B</team>
        </cyclist>
    </race>
</start_list>"""

    def test_generate_start_list_xml(self):
        # Test the XML generation function
        xml_output = generate_start_list_xml(self.race_data)
        self.assertEqual(xml_output.strip(), self.expected_xml_structure.strip())

    def test_empty_cyclists(self):
        # Test the XML generation with no cyclists
        empty_race_data = {
            'race_name': 'Tour de France',
            'race_year': 2024,
            'cyclists': []
        }
        expected_empty_xml = """<start_list>
    <race name="Tour de France" year="2024">
    </race>
</start_list>"""
        xml_output = generate_start_list_xml(empty_race_data)
        self.assertEqual(xml_output.strip(), expected_empty_xml.strip())

if __name__ == '__main__':
    unittest.main()