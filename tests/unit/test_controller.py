import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from unittest.mock import AsyncMock
from app.models.types import SwiftCodeBase

class TestSwiftCodeController:
    
    def test_validate_swift_code_valid(self, swift_controller):
        assert swift_controller.validate_swift_code("ABCDEFG123") == True
        assert swift_controller.validate_swift_code("ABCDXXX") == True
    
    def test_validate_swift_code_invalid(self, swift_controller):
        with pytest.raises(ValueError):
            swift_controller.validate_swift_code("AB")
        
        with pytest.raises(ValueError):
            swift_controller.validate_swift_code("abcdefg123")
        
        with pytest.raises(ValueError):
            swift_controller.validate_swift_code("ABC DEF12") 
    
    def test_is_headquarters(self, swift_controller):
        assert swift_controller.is_headquarters("ABCDXXX") == True
        assert swift_controller.is_headquarters("ABCD123") == False
    
    @pytest.mark.asyncio
    async def test_get_swift_code(self, swift_controller):
        mock_result = {
            "swift_code": "CTRLTEST123",
            "bank_name": "Controller Test Bank",
            "address": "123 Controller St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True,
            "branches": []
        }
        swift_controller.swift_service.get_swift_code = AsyncMock(return_value=mock_result)
        
        result = await swift_controller.get_swift_code("CTRLTEST123")
        
        assert result == mock_result
        swift_controller.swift_service.get_swift_code.assert_called_once_with("CTRLTEST123")
    
    @pytest.mark.asyncio
    async def test_get_swift_code_not_found(self, swift_controller):
        """Test get_swift_code with non-existent code."""
        swift_controller.swift_service.get_swift_code = AsyncMock(return_value=None)
        
        with pytest.raises(HTTPException) as excinfo:
            await swift_controller.get_swift_code("NONEXISTENT")
        
        assert excinfo.value.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_swift_code(self, swift_controller):
        swift_controller.swift_service.get_swift_code = AsyncMock(return_value=None)
        swift_controller.swift_service.create_swift_code = AsyncMock()
        
        swift_data = SwiftCodeBase(
            swift_code="CREATETEST",
            bank_name="Create Test Bank",
            address="123 Create St",
            country_iso2="US",
            country_name="UNITED STATES",
            is_headquarters=True
        )
        
        result = await swift_controller.create_swift_code(swift_data)
        
        assert result["message"] == "SWIFT code CREATETEST created successfully"
        swift_controller.swift_service.create_swift_code.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_swift_code_duplicate(self, swift_controller):
        mock_existing = {
            "swift_code": "DUPLICATE",
            "bank_name": "Duplicate Bank",
            "address": "123 Dupe St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True
        }
        swift_controller.swift_service.get_swift_code = AsyncMock(return_value=mock_existing)
        
        swift_data = SwiftCodeBase(
            swift_code="DUPLICATE",
            bank_name="New Dupe Bank",
            address="456 Dupe St",
            country_iso2="US",
            country_name="UNITED STATES",
            is_headquarters=True
        )
        
        with pytest.raises(HTTPException) as excinfo:
            await swift_controller.create_swift_code(swift_data)
        
        assert excinfo.value.status_code == 409