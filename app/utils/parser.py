import pandas as pd
from typing import List, Dict, Any
import logging

class SwiftCodeParser:
    def __init__(self, filePath: str):
        self.filePath = filePath

    def parse(self) -> List[Dict[str, Any]]:
        try:
            df = pd.read_excel(self.filePath)
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            requiredColumns = ['country_iso2_code', 'swift_code', 'name', 'address', 'country_name']

            for col in requiredColumns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' is missing in the file.")
            
            result = []

            for _, row in df.iterrows():
                countryISO2 = row['country_iso2_code'].strip().upper()
                countryName = row['country_name'].strip().upper()
                swiftCode = row['swift_code'].strip().upper()

                isHeadquarters = swiftCode.endswith('XXX')

                entry = {
                    'swiftCode': swiftCode,
                    'bankName': row['name'].strip(),
                    'address': row['address'].strip(),
                    'countryISO2': countryISO2,
                    'countryName': countryName,
                    'isHeadquarters': isHeadquarters
                }

                result.append(entry)

            return result
        except Exception as e:
            logging.error(f"Error parsing file: {e}")
            raise  # Re-raise after logging
        
        return []
    
    def getHeadquartersMap(self, swiftData: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        hqMap = {}

        for entry in swiftData:
            if entry['isHeadquarters']:
                hqCode = entry['swiftCode']
                hqMap[hqCode] = []

        for entry in swiftData:
            if not entry['isHeadquarters']:
                # Change to -3 to match the service class
                potentialHq = entry['swiftCode'][:-3] + 'XXX'

                if potentialHq in hqMap:
                    branchData = entry.copy()
                    hqMap[potentialHq].append(branchData)
        
        return hqMap
