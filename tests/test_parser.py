import unittest
import os
import pandas as pd
from app.utils.parser import SwiftCodeParser


class TestSwiftCodeParser(unittest.TestCase):
    def setUp(self):
        # Create a temporary Excel file
        df = pd.DataFrame({
            'country_iso2_code': ['US', 'US'],
            'swift_code': ['ABCDUSXXX', 'ABCDUS33XXX'],
            'name': ['Test Bank HQ', 'Test Bank Branch'],
            'address': ['123 Main Street', '456 Side Street'],
            'country_name': ['United States', 'United States']
        })
        
        self.test_file = 'test_swift_codes.xlsx'
        df.to_excel(self.test_file, index=False)
        
    def tearDown(self):
        # Clean up the test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_parse(self):
        parser = SwiftCodeParser(self.test_file)
        result = parser.parse()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['swift_code'], 'ABCDUSXXX')
        self.assertEqual(result[0]['country_iso2'], 'US')
        self.assertEqual(result[0]['is_headquarters'], True)
        
        self.assertEqual(result[1]['swift_code'], 'ABCDUS33XXX')
        self.assertEqual(result[1]['country_iso2'], 'US')
        
    def test_get_headquarters_map(self):
        # Create data with proper branch relationship
        df = pd.DataFrame({
            'country_iso2_code': ['US', 'US'],
            'swift_code': ['ABCDUSXXX', 'ABCDUS33XXX'],
            'name': ['Test Bank HQ', 'Test Bank Branch'],
            'address': ['123 Main Street', '456 Side Street'],
            'country_name': ['United States', 'United States']
        })
        
        df.to_excel(self.test_file, index=False)
        
        parser = SwiftCodeParser(self.test_file)
        swift_data = parser.parse()
        hq_map = parser.get_headquarters_map(swift_data)
        
        # Test that headquarters mapping works
        self.assertIn('ABCDUSXXX', hq_map)
        
        # Create a specific assertion based on your logic
        # If your logic expects the first 8 characters to match:
        if 'ABCDUS33XXX'[:8] == 'ABCDUSXXX'[:8]:
            self.assertEqual(len(hq_map['ABCDUSXXX']), 1)
        else:
            # If different logic applies, adjust your assertion
            potential_hq = 'ABCDUS33XXX'[:-3] + 'XXX'
            if potential_hq == 'ABCDUSXXX':
                self.assertEqual(len(hq_map['ABCDUSXXX']), 1)
            else:
                self.assertEqual(len(hq_map['ABCDUSXXX']), 0)

    def test_empty_file(self):
        """Test parsing an empty Excel file."""
        # Create an empty Excel file
        df = pd.DataFrame()
        df.to_excel(self.test_file, index=False)
        
        parser = SwiftCodeParser(self.test_file)
        
        # This should raise an error because required columns are missing
        with self.assertRaises(ValueError):
            parser.parse()

    def test_missing_required_columns(self):
        """Test parsing a file with missing required columns."""
        # Create a file with some but not all required columns
        df = pd.DataFrame({
            'swift_code': ['ABCDUSXXX'],
            'name': ['Test Bank']
            # Missing country_iso2_code, address, and country_name
        })
        
        df.to_excel(self.test_file, index=False)
        
        parser = SwiftCodeParser(self.test_file)
        
        # This should raise an error
        with self.assertRaises(ValueError):
            parser.parse()

    def test_mixed_case_handling(self):
        """Test that the parser handles mixed case correctly."""
        # Create data with mixed case
        df = pd.DataFrame({
            'country_iso2_code': ['us', 'Us'],  # lowercase
            'swift_code': ['abcdusXXX', 'ABCDus33XXX'],  # mixed case
            'name': ['Test Bank HQ', 'Test Bank Branch'],
            'address': ['123 Main Street', '456 Side Street'],
            'country_name': ['united states', 'United States']  # mixed case
        })
        
        df.to_excel(self.test_file, index=False)
        
        parser = SwiftCodeParser(self.test_file)
        result = parser.parse()
        
        # Check that everything was converted to uppercase
        self.assertEqual(result[0]['swift_code'], 'ABCDUSXXX')
        self.assertEqual(result[0]['country_iso2'], 'US')
        self.assertEqual(result[0]['country_name'], 'UNITED STATES')
        
        self.assertEqual(result[1]['swift_code'], 'ABCDUS33XXX')
        self.assertEqual(result[1]['country_iso2'], 'US')
        self.assertEqual(result[1]['country_name'], 'UNITED STATES')

    def test_special_characters(self):
        """Test handling of special characters in the data."""
        # Create data with special characters
        df = pd.DataFrame({
            'country_iso2_code': ['FR', 'DE'],
            'swift_code': ['SPÉCFRXX', 'SONDERDEXX'],
            'name': ['Banque Spéciale', 'Sonderzeichen Bank'],
            'address': ['123 Rue Café', 'Straße 456'],
            'country_name': ['France', 'Germany']
        })
        
        df.to_excel(self.test_file, index=False)
        
        parser = SwiftCodeParser(self.test_file)
        result = parser.parse()
        
        # Check that special characters are preserved where appropriate
        self.assertEqual(result[0]['bank_name'], 'Banque Spéciale')
        self.assertEqual(result[0]['address'], '123 Rue Café')
        
        self.assertEqual(result[1]['bank_name'], 'Sonderzeichen Bank')
        self.assertEqual(result[1]['address'], 'Straße 456')

if __name__ == '__main__':
    unittest.main()