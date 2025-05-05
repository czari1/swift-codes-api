import pytest
from app.utils.parser import SwiftCodeParser

class TestSwiftCodeParser:
    
    def test_parse_excel_file(self, create_test_excel):
        """Test parsing valid Excel file."""
        parser = SwiftCodeParser(create_test_excel)
        result = parser.parse_files()
        
        assert len(result) == 3
        assert result[0]["swift_code"] == "AAAAUSXXXXX"
        assert result[0]["is_headquarters"] == True
        assert result[1]["is_headquarters"] == False
        assert result[2]["country_iso2"] == "GB"
    
    def test_parse_csv_file(self, create_test_csv):
        """Test parsing valid CSV file."""
        parser = SwiftCodeParser(create_test_csv)
        result = parser.parse_files()
        
        assert len(result) == 3
        assert result[0]["swift_code"] == "AAAAUSXXXXX"
        assert result[1]["bank_name"] == "Test Bank Branch"
    
    def test_invalid_file_format(self):
        """Test handling invalid file formats."""
        with pytest.raises(ValueError) as excinfo:
            parser = SwiftCodeParser("test_file.txt")
            parser.parse_files()
        
        assert "Not a valid file type" in str(excinfo.value)
    
    def test_file_not_found(self):
        """Test handling non-existent file."""
        with pytest.raises(Exception):
            parser = SwiftCodeParser("nonexistent_file.xlsx")
            parser.parse_files()
    
    def test_invalid_file_structure(self, invalid_test_excel):
        """Test handling Excel file with missing columns."""
        with pytest.raises(ValueError) as excinfo:
            parser = SwiftCodeParser(invalid_test_excel)
            parser.parse_files()
        
        assert "Required column" in str(excinfo.value)
    
    def test_headquarters_mapping(self, create_test_excel):
        """Test headquarters mapping functionality."""
        parser = SwiftCodeParser(create_test_excel)
        swift_data = parser.parse_files()
        hq_map = parser.get_headquarters_map(swift_data)
        
        assert "AAAAUSXXXXX" in hq_map
        assert len(hq_map["AAAAUSXXXXX"]) == 0  
        assert "BBBBGBXXXXX" in hq_map
        assert len(hq_map["BBBBGBXXXXX"]) == 0