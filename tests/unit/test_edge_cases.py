import pytest
from unittest.mock import MagicMock
import pandas as pd
import os
from app.utils.parser import SwiftCodeParser

class TestEdgeCases:
    
    def test_empty_file(self, tmp_path):
        """Test handling of empty files."""
        # Create empty Excel file
        file_path = tmp_path / "empty.xlsx"
        df = pd.DataFrame()
        df.to_excel(file_path, index=False)
        
        parser = SwiftCodeParser(str(file_path))
        
        with pytest.raises(Exception):
            parser.parse_files()
    
    def test_case_insensitivity(self, swift_repository):
        """Test case insensitivity of SWIFT code lookups."""
        # Add a code with uppercase
        swift_data = {
            "swift_code": "CASETEST123",
            "bank_name": "Case Test Bank",
            "address": "123 Case St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True
        }
        
        swift_repository.create_swift_code(swift_data)
        
        # Look up with lowercase
        result = swift_repository.get_swift_code("casetest123")
        
        assert result is not None
        assert result["swift_code"] == "CASETEST123"
    
    def test_special_characters_in_bank_name(self, swift_repository):
        """Test handling of special characters in bank names."""
        swift_data = {
            "swift_code": "SPECIAL123",
            "bank_name": "Special & Chars Bank (Pty) Ltd.",
            "address": "123 Special St",
            "country_iso2": "ZA",
            "country_name": "SOUTH AFRICA",
            "is_headquarters": True
        }
        
        swift_repository.create_swift_code(swift_data)
        result = swift_repository.get_swift_code("SPECIAL123")
        
        assert result is not None
        assert result["bank_name"] == "Special & Chars Bank (Pty) Ltd."
    
    def test_maximum_swift_code_length(self, swift_repository):
        """Test handling of maximum length SWIFT codes."""
        swift_data = {
            "swift_code": "ABCDEFGHIJK",  # 11 chars
            "bank_name": "Max Length Bank",
            "address": "123 Max St",
            "country_iso2": "DE",
            "country_name": "GERMANY",
            "is_headquarters": False
        }
        
        swift_repository.create_swift_code(swift_data)
        result = swift_repository.get_swift_code("ABCDEFGHIJK")
        
        assert result is not None
    
    def test_minimum_swift_code_length(self, swift_controller):
        """Test handling of minimum length SWIFT codes."""
        # Test minimum valid length (4)
        assert swift_controller.validate_swift_code("ABCD") == True
        
        # Test too short
        with pytest.raises(ValueError):
            swift_controller.validate_swift_code("ABC")
    
    def test_non_ascii_characters(self, swift_repository):
        """Test handling of non-ASCII characters in data."""
        swift_data = {
            "swift_code": "NONASCII1",
            "bank_name": "Münchner Bank",  # German umlaut
            "address": "123 München St",
            "country_iso2": "DE",
            "country_name": "GERMANY",
            "is_headquarters": True
        }
        
        swift_repository.create_swift_code(swift_data)
        result = swift_repository.get_swift_code("NONASCII1")
        
        assert result is not None
        assert "Münchner" in result["bank_name"]