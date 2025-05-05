from unittest.mock import patch
from fastapi import HTTPException

def test_health_endpoint(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_swift_code(test_client):
    mock_swift_code = {
        "swift_code": "TESTAPI123",
        "bank_name": "API Test Bank",
        "address": "123 API St",
        "country_iso2": "US",
        "country_name": "UNITED STATES",
        "is_headquarters": True,
        "branches": []
    }
    
    with patch("app.controllers.swift_controllers.SwiftCodeController.get_swift_code", 
               return_value=mock_swift_code):
        response = test_client.get("/v1/swift-codes/TESTAPI123")
        
        assert response.status_code == 200
        assert response.json()["swift_code"] == "TESTAPI123"

def test_get_swift_code_not_found(test_client):
    with patch("app.controllers.swift_controllers.SwiftCodeController.get_swift_code", 
               side_effect=HTTPException(status_code=404, detail="Not found")):
        response = test_client.get("/v1/swift-codes/NONEXISTENT")
        
        assert response.status_code == 404

def test_create_swift_code(test_client):
    with patch("app.controllers.swift_controllers.SwiftCodeController.create_swift_code", 
               return_value={"message": "SWIFT code APICREATE created successfully"}):
        swift_data = {
            "swift_code": "APICREATE",
            "bank_name": "API Create Bank",
            "address": "123 API Create St",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True
        }
        
        response = test_client.post("/v1/swift-codes/", json=swift_data)
        
        assert response.status_code == 200
        assert "created successfully" in response.json()["message"]

def test_create_swift_code_invalid(test_client):
    swift_data = {
        "swift_code": "INCOMPLETE",
    }
    
    response = test_client.post("/v1/swift-codes/", json=swift_data)
    
    assert response.status_code == 422 