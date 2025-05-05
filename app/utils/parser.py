import pandas as pd
from typing import List, Dict, Any
import logging
import os

class SwiftCodeParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_extension = os.path.splitext(file_path)[1].lower()


    def parse_files(self) -> List[Dict[str, Any]]:
        """
        Parse SWIFT codes from file. Despite the name, this method handles both Excel and CSV.
        """
        try:
            if self.file_extension == '.csv':
                df = pd.read_csv(self.file_path)
                logging.info(f"Parsing CSV file: {self.file_path}")
            elif self.file_extension in ['.xlsx', '.xls']:
                df = pd.read_excel(self.file_path)
                logging.info(f"Parsing Excel file: {self.file_path}")
            else:
                raise ValueError(f"Not a valid file type: {self.file_extension}. Only .csv and .xlsx are supported.")
            
            df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

            required_columns = ['country_iso2_code', 'swift_code', 'name', 'address', 'country_name']

            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' is missing in the file.")
            
            swift_data = []

            for _, row in df.iterrows():
                country_iso2 = row['country_iso2_code'].strip().upper()
                country_name = row['country_name'].strip().upper()
                swift_code = row['swift_code'].strip().upper()

                is_headquarters = swift_code.endswith('XXX')

                entry = {
                    'swift_code': swift_code,
                    'bank_name': row['name'].strip(),
                    'address': row['address'].strip(),
                    'country_iso2': country_iso2,
                    'country_name': country_name,
                    'is_headquarters': is_headquarters
                }

                swift_data.append(entry)


            logging.info(f"Successfully parsed {len(swift_data)} SWIFT codes from {self.file_path}")
            return swift_data

        except Exception as e:
            logging.error(f"Error parsing file: {e}")
            raise  
    
    def get_headquarters_map(self, swift_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create a mapping of headquarters SWIFT codes to their branch offices.
        """
        hq_map = {}

        for entry in swift_data:
            if entry['is_headquarters']:
                hq_code = entry['swift_code']
                hq_map[hq_code] = []

        for entry in swift_data:
            if not entry['is_headquarters']:
                potential_hq = entry['swift_code'][:-3] + 'XXX'
                
                if potential_hq in hq_map:
                    branch_data = entry.copy()
                    hq_map[potential_hq].append(branch_data)
        
        return hq_map
