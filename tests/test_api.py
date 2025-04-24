import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, getDB
from app.models import SwiftCode, BranchAssociation
import uuid

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    
    db = next(getDB())
    
    # Add test data
    hq = SwiftCode(
        swiftCode="TESTUSXXX",
        bankName="TEST BANK HQ",
        address="123 MAIN ST",
        countryISO2="US",
        countryName="UNITED STATES",
        isHeadquarters=True
    )
    
    branch = SwiftCode(
        swiftCode="TESTUS33XXX",
        bankName="TEST BANK BRANCH",
        address="456 SIDE ST",
        countryISO2="US",
        countryName="UNITED STATES",
        isHeadquarters=False
    )
    
    db.add(hq)
    db.add(branch)
    db.commit()
    
    association = BranchAssociation(
        id=str(uuid.uuid4()),
        headquarterSwift=hq.swiftCode,
        branchSwift=branch.swiftCode
    )
    
    db.add(association)
    db.commit()
    
    yield db
    
    # Clean up
    db.query(BranchAssociation).delete()
    db.query(SwiftCode).delete()
    db.commit()

def test_get_swift_code(test_db):
    response = client.get("/v1/swift-codes/TESTUSXXX")
    assert response.status_code == 200
    data = response.json()
    assert data["swiftCode"] == "TESTUSXXX"
    assert data["isHeadquarters"] == True
    # Only check for branches if the SWIFT code is a headquarters
    if data["isHeadquarters"]:
        assert "branches" in data
    
def test_get_nonexistent_swift_code():
    response = client.get("/v1/swift-codes/NONEXISTENT")
    assert response.status_code == 404
    
def test_get_country_swift_codes(test_db):
    response = client.get("/v1/swift-codes/country/US")
    assert response.status_code == 200
    data = response.json()
    assert data["countryISO2"] == "US"
    assert data["countryName"] == "UNITED STATES"
    assert len(data["swiftCodes"]) > 0

def test_create_swift_code(test_db):
    new_code = {
        "swiftCode": "NEWCODEXXX",
        "bankName": "NEW BANK",
        "address": "NEW ADDRESS",
        "countryISO2": "FR",
        "countryName": "FRANCE",
        "isHeadquarters": True
    }
    
    response = client.post("/v1/swift-codes/", json=new_code)
    assert response.status_code == 200
    
    # Verify it was created
    check_response = client.get("/v1/swift-codes/NEWCODEXXX")
    assert check_response.status_code == 200
    
def test_delete_swift_code(test_db):
    # Create a code to delete
    new_code = {
        "swiftCode": "DELETEMEXXX",
        "bankName": "DELETE BANK",
        "address": "DELETE ADDRESS",
        "countryISO2": "IT",
        "countryName": "ITALY",
        "isHeadquarters": True
    }
    
    client.post("/v1/swift-codes/", json=new_code)
    
    # Delete it
    response = client.delete("/v1/swift-codes/DELETEMEXXX")
    assert response.status_code == 200
    
    # Verify it was deleted
    check_response = client.get("/v1/swift-codes/DELETEMEXXX")
    assert check_response.status_code == 404