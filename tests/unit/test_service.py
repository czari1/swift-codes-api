import pytest
from unittest.mock import MagicMock

class TestSwiftCodeService:
    
    @pytest.mark.asyncio
    async def test_get_swift_code(self, swift_service):
        swift_service.swift_code_repository.get_swift_code = MagicMock(return_value={
            "swift_code": "TESTSERVICE",
            "bank_name": "Service Test Bank",
            "address": "123 Service St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True,
            "branches": []
        })
        
        result = await swift_service.get_swift_code("TESTSERVICE")
        
        assert result is not None
        assert result["swift_code"] == "TESTSERVICE"
        swift_service.swift_code_repository.get_swift_code.assert_called_once_with("TESTSERVICE")
    
    @pytest.mark.asyncio
    async def test_get_swift_code_not_found(self, swift_service):
        swift_service.swift_code_repository.get_swift_code = MagicMock(return_value=None)
        
        result = await swift_service.get_swift_code("NONEXISTENT")
        
        assert result is None
        swift_service.swift_code_repository.get_swift_code.assert_called_once_with("NONEXISTENT")
    
    @pytest.mark.asyncio
    async def test_create_swift_code(self, swift_service):
        mock_result = MagicMock()
        swift_service.swift_code_repository.create_swift_code = MagicMock(return_value=mock_result)
        
        swift_data = {
            "swift_code": "NEWSERVICE",
            "bank_name": "New Service Bank",
            "address": "123 New St",
            "country_iso2": "CA",
            "country_name": "CANADA",
            "is_headquarters": True
        }
        
        result = await swift_service.create_swift_code(swift_data)
        
        assert result == mock_result
        swift_service.swift_code_repository.create_swift_code.assert_called_once_with(swift_data)