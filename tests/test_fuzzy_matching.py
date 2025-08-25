"""
Test cases for fuzzy matching functionality in model_api.py
"""

import unittest
import os
import tempfile
import pandas as pd
from src.model.model_api import fuzzy_match_race_names
from src.utils import commons


class TestFuzzyMatching(unittest.TestCase):
    """Test class for fuzzy matching race names functionality"""

    def setUp(self):
        """Set up test data"""
        # Sample PCM race data
        self.pcm_races_sample = [
            {'id': 1, 'name': 'Tour de France'},
            {'id': 2, 'name': 'Giro d\'Italia'},
            {'id': 3, 'name': 'Vuelta a España'},
            {'id': 4, 'name': 'Paris-Roubaix'},
            {'id': 5, 'name': 'Milano-Sanremo'},
            {'id': 6, 'name': 'Liège-Bastogne-Liège'},
            {'id': 7, 'name': 'Tour de Suisse'},
            {'id': 8, 'name': 'Criterium du Dauphine'},
            {'id': 9, 'name': 'Amstel Gold Race'},
            {'id': 10, 'name': 'Some Unknown Race'}
        ]

        # Sample URL race data (with slight variations to test fuzzy matching)
        self.url_races_sample = [
            {'id': 1, 'name': 'Tour de France', 'url': 'race/tour-de-france'},
            {'id': 2, 'name': 'Giro d\'Italia', 'url': 'race/giro-d-italia'},
            {'id': 3, 'name': 'La Vuelta ciclista a España', 'url': 'race/vuelta-a-espana'},
            {'id': 4, 'name': 'Paris-Roubaix', 'url': 'race/paris-roubaix'},
            {'id': 5, 'name': 'Milano-SanRemo', 'url': 'race/milano-sanremo'},
            {'id': 6, 'name': 'Liège-Bastogne-Liège', 'url': 'race/liege-bastogne-liege'},
            {'id': 7, 'name': 'Tour de Suisse', 'url': 'race/tour-de-suisse'},
            {'id': 8, 'name': 'Critérium du Dauphiné', 'url': 'race/dauphine'},
            {'id': 9, 'name': 'Amstel Gold Race', 'url': 'race/amstel-gold-race'},
            {'id': 10, 'name': 'Vuelta▼', 'url': 'race/vuelta-a-espana/2025'},  # Navigation item
            {'id': 11, 'name': 'Startlist', 'url': 'race/vuelta-a-espana/2025/startlist'},  # Navigation item
            {'id': 12, 'name': 'Different Race Name', 'url': 'race/different-race'}
        ]

    def test_fuzzy_match_basic_functionality(self):
        """Test basic fuzzy matching functionality"""
        matches_df, unmatched_df = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=80
        )
        
        # Check that we get DataFrames back
        self.assertIsInstance(matches_df, pd.DataFrame)
        self.assertIsInstance(unmatched_df, pd.DataFrame)
        
        # Check that we have some matches
        self.assertGreater(len(matches_df), 0, "Should have at least some matches")
        
        # Check required columns in matches DataFrame
        expected_match_columns = ['pcm_id', 'pcm_race_name', 'url_id', 'url_race_name', 
                                'url_path', 'confidence', 'match_method']
        for col in expected_match_columns:
            self.assertIn(col, matches_df.columns, f"Missing column: {col}")
        
        # Check required columns in unmatched DataFrame
        expected_unmatched_columns = ['pcm_id', 'pcm_race_name', 'best_match_name', 
                                    'best_confidence', 'best_method']
        for col in expected_unmatched_columns:
            self.assertIn(col, unmatched_df.columns, f"Missing column: {col}")

    def test_exact_matches(self):
        """Test that exact matches are found with high confidence"""
        matches_df, _ = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=50
        )
        
        # Check for exact matches
        exact_matches = matches_df[matches_df['pcm_race_name'] == matches_df['url_race_name']]
        self.assertGreater(len(exact_matches), 0, "Should find exact matches")
        
        # Check that exact matches have high confidence
        for _, match in exact_matches.iterrows():
            self.assertGreaterEqual(match['confidence'], 90, 
                                  f"Exact match should have high confidence: {match['pcm_race_name']}")

    def test_fuzzy_matches(self):
        """Test that fuzzy matches work for similar but not identical names"""
        matches_df, _ = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=60
        )
        
        # Look for the Vuelta match (different naming)
        vuelta_matches = matches_df[matches_df['pcm_race_name'] == 'Vuelta a España']
        self.assertGreater(len(vuelta_matches), 0, "Should match Vuelta despite different naming")
        
        # Look for Milano-Sanremo vs Milano-SanRemo
        milano_matches = matches_df[matches_df['pcm_race_name'] == 'Milano-Sanremo']
        self.assertGreater(len(milano_matches), 0, "Should match Milano-Sanremo variants")

    def test_navigation_items_filtered(self):
        """Test that navigation items are filtered out"""
        matches_df, _ = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=50
        )
        
        # Check that no matches are against navigation items
        navigation_matches = matches_df[
            matches_df['url_race_name'].str.lower().isin(['vuelta▼', 'startlist', 'palmares'])
        ]
        self.assertEqual(len(navigation_matches), 0, "Should not match against navigation items")

    def test_confidence_threshold(self):
        """Test that confidence threshold is respected"""
        # Test with high confidence threshold
        matches_high, unmatched_high = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=95
        )
        
        # Test with low confidence threshold
        matches_low, unmatched_low = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=50
        )
        
        # Higher threshold should result in fewer matches
        self.assertGreaterEqual(len(matches_low), len(matches_high), 
                              "Lower threshold should yield more matches")
        
        # All matches should meet the confidence threshold
        for _, match in matches_high.iterrows():
            self.assertGreaterEqual(match['confidence'], 95, 
                                  "All matches should meet confidence threshold")

    def test_empty_lists(self):
        """Test behavior with empty input lists"""
        # Test with empty PCM races
        matches_df, unmatched_df = fuzzy_match_race_names([], self.url_races_sample)
        self.assertEqual(len(matches_df), 0)
        self.assertEqual(len(unmatched_df), 0)
        
        # Test with empty URL races
        matches_df, unmatched_df = fuzzy_match_race_names(self.pcm_races_sample, [])
        self.assertEqual(len(matches_df), 0)
        self.assertEqual(len(unmatched_df), len(self.pcm_races_sample))

    def test_match_methods_included(self):
        """Test that match methods are properly recorded"""
        matches_df, _ = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=60
        )
        
        if not matches_df.empty:
            # Check that match_method is recorded for all matches
            self.assertTrue(all(matches_df['match_method'].notna()), 
                          "All matches should have a match method recorded")
            
            # Check that match methods are from expected set
            valid_methods = {'ratio', 'partial_ratio', 'token_sort_ratio', 'token_set_ratio'}
            for method in matches_df['match_method'].unique():
                self.assertIn(method, valid_methods, f"Invalid match method: {method}")

    def test_url_path_extraction(self):
        """Test that URL paths are correctly extracted"""
        matches_df, _ = fuzzy_match_race_names(
            self.pcm_races_sample, 
            self.url_races_sample, 
            confidence_threshold=60
        )
        
        if not matches_df.empty:
            # Check that URL paths are present
            self.assertTrue(all(matches_df['url_path'].notna()), 
                          "All matches should have URL paths")
            
            # Check that URL paths look reasonable
            for _, match in matches_df.iterrows():
                url_path = match['url_path']
                self.assertTrue(isinstance(url_path, str), "URL path should be a string")
                self.assertGreater(len(url_path), 0, "URL path should not be empty")


class TestFuzzyMatchingIntegration(unittest.TestCase):
    """Integration tests for fuzzy matching with real data structures"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_data_structure_compatibility(self):
        """Test that the function works with realistic data structures"""
        # Create data that matches the expected structure from database queries
        pcm_races = [
            {'id': 1, 'name': 'Tour de France'},
            {'id': 2, 'name': 'Giro d\'Italia'},
            {'id': 3, 'name': 'Vuelta a España'}
        ]
        
        url_races = [
            {'id': 1, 'name': 'Tour de France', 'url': 'race/tour-de-france'},
            {'id': 2, 'name': 'Giro d\'Italia', 'url': 'race/giro-d-italia'},
            {'id': 3, 'name': 'La Vuelta ciclista a España', 'url': 'race/vuelta-a-espana'}
        ]
        
        matches_df, unmatched_df = fuzzy_match_race_names(pcm_races, url_races)
        
        # Should find matches for all races
        self.assertGreaterEqual(len(matches_df), 2, "Should find at least 2 matches")
        
        # Check that the structure is correct for database updates
        for _, match in matches_df.iterrows():
            self.assertIn('pcm_id', match.index)
            self.assertIn('url_path', match.index)
            self.assertIsInstance(match['pcm_id'], (int, float))
            self.assertIsInstance(match['url_path'], str)


if __name__ == '__main__':
    unittest.main()
