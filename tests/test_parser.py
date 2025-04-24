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
        self.assertEqual(result[0]['swiftCode'], 'ABCDUSXXX')
        self.assertEqual(result[0]['countryISO2'], 'US')
        self.assertEqual(result[0]['isHeadquarters'], True)
        
        self.assertEqual(result[1]['swiftCode'], 'ABCDUS33XXX')
        self.assertEqual(result[1]['countryISO2'], 'US')
        
    def test_getHeadquartersMap(self):
        # Create data with proper branch relationship
        df = pd.DataFrame({
            'country_iso2_code': ['US', 'US'],
            'swift_code': ['ABCDUSXXX', 'ABCDUS33XXX'],  # This needs to match the pattern
            'name': ['Test Bank HQ', 'Test Bank Branch'],
            'address': ['123 Main Street', '456 Side Street'],
            'country_name': ['United States', 'United States']
        })
        
        df.to_excel(self.test_file, index=False)
        
        parser = SwiftCodeParser(self.test_file)
        swift_data = parser.parse()
        hq_map = parser.getHeadquartersMap(swift_data)
        
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

if __name__ == '__main__':
    unittest.main()