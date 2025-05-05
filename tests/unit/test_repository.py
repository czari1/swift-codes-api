import pytest
from app.models.swift_code import SwiftCode
from app.models.branch_association import BranchAssociation

class TestSwiftCodeRepository:
    
    def test_get_swift_code_nonexistent(self, swift_repository):
        """Test getting a non-existent SWIFT code."""
        result = swift_repository.get_swift_code("NONEXISTENT")
        assert result is None
    
    def test_create_and_get_swift_code(self, swift_repository):
        """Test creating and getting a SWIFT code."""
        swift_data = {
            "swift_code": "TESTCODE123",
            "bank_name": "Test Bank",
            "address": "123 Test St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True
        }

        swift_repository.create_swift_code(swift_data)

        result = swift_repository.get_swift_code("TESTCODE123")
        
        assert result is not None
        assert result["swift_code"] == "TESTCODE123"
        assert result["bank_name"] == "Test Bank"
        assert result["is_headquarters"] == True
    
    def test_create_duplicate_swift_code(self, swift_repository):
        """Test handling duplicate SWIFT codes."""
        swift_data = {
            "swift_code": "DUPECODE123",
            "bank_name": "Dupe Bank",
            "address": "123 Dupe St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True
        }

        swift_repository.create_swift_code(swift_data)

        with pytest.raises(ValueError) as excinfo:
            swift_repository.create_swift_code(swift_data)
        
        assert "already exists" in str(excinfo.value)
    
    def test_delete_swift_code(self, swift_repository):
        """Test deleting a SWIFT code."""
        swift_data = {
            "swift_code": "DELETEME123",
            "bank_name": "Delete Bank",
            "address": "123 Delete St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": False
        }
        
        swift_repository.create_swift_code(swift_data)

        assert swift_repository.get_swift_code("DELETEME123") is not None

        result = swift_repository.delete_swift_code("DELETEME123")
        assert result == True

        assert swift_repository.get_swift_code("DELETEME123") is None

        result = swift_repository.delete_swift_code("NONEXISTENT")
        assert result == False
    
    def test_get_country_swift_codes(self, swift_repository):
        """Test getting SWIFT codes by country."""
        swift_data1 = {
            "swift_code": "FRCODE1234",
            "bank_name": "French Bank 1",
            "address": "123 Paris St",
            "country_iso2": "FR",
            "country_name": "FRANCE",
            "is_headquarters": True
        }
        
        swift_data2 = {
            "swift_code": "FRCODE5678",
            "bank_name": "French Bank 2",
            "address": "456 Lyon St",
            "country_iso2": "FR",
            "country_name": "FRANCE",
            "is_headquarters": False
        }
        
        swift_repository.create_swift_code(swift_data1)
        swift_repository.create_swift_code(swift_data2)

        result = swift_repository.get_country_swift_codes("FR")
        
        assert result is not None
        assert result["country_iso2"] == "FR"
        assert result["country_name"] == "FRANCE"
        assert len(result["swift_codes"]) == 2

        result = swift_repository.get_country_swift_codes("XX")
        
        assert result is not None
        assert result["country_iso2"] == "XX"
        assert result["country_name"] == ""
        assert len(result["swift_codes"]) == 0
    
    def test_bulk_create_swift_codes(self, swift_repository):
        """Test bulk creation of SWIFT codes."""
        swift_data = [
            {
                "swift_code": "BULK1USXXX",
                "bank_name": "Bulk Test Bank HQ",
                "address": "123 Bulk St",
                "country_iso2": "US",
                "country_name": "UNITED STATES",
                "is_headquarters": True
            },
            {
                "swift_code": "BULK1US123",
                "bank_name": "Bulk Test Branch",
                "address": "456 Bulk St",
                "country_iso2": "US",
                "country_name": "UNITED STATES",
                "is_headquarters": False
            }
        ]

        branch_map = {"BULK1USXXX": ["BULK1US123"]}
        
        swift_repository.bulk_create_swift_codes(swift_data, branch_map)

        result1 = swift_repository.get_swift_code("BULK1USXXX")
        result2 = swift_repository.get_swift_code("BULK1US123")
        
        assert result1 is not None
        assert result2 is not None

        assert len(result1["branches"]) == 1
        assert result1["branches"][0]["swift_code"] == "BULK1US123"