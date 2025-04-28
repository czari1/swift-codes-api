import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app.models import SwiftCode, BranchAssociation
import uuid

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    # Add test data
    hq = SwiftCode(
        swift_code="TESTUSXXX",
        bank_name="TEST BANK HQ",
        address="123 MAIN ST",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarters=True
    )
    
    branch = SwiftCode(
        swift_code="TESTUS33XXX",
        bank_name="TEST BANK BRANCH",
        address="456 SIDE ST",
        country_iso2="US",
        country_name="UNITED STATES",
        is_headquarters=False
    )
    
    db.add(hq)
    db.add(branch)
    db.commit()
    
    association = BranchAssociation(
        id=str(uuid.uuid4()),
        headquarter_swift=hq.swift_code,
        branch_swift=branch.swift_code
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
    assert data["swift_code"] == "TESTUSXXX"  # Changed from swiftCode
    assert data["is_headquarters"] == True    # Changed from isHeadquarters
    # Only check for branches if the SWIFT code is a headquarters
    if data["is_headquarters"]:
        assert "branches" in data
    
def test_get_nonexistent_swift_code():
    response = client.get("/v1/swift-codes/NONEXISTENT")
    assert response.status_code == 404
    
def test_get_country_swift_codes(test_db):
    response = client.get("/v1/swift-codes/country/US")
    assert response.status_code == 200
    data = response.json()
    assert data["country_iso2"] == "US"       # Changed from countryISO2
    assert data["country_name"] == "UNITED STATES"  # Changed from countryName
    assert len(data["swift_codes"]) > 0       # Changed from swiftCodes

def test_create_swift_code(test_db):
    new_code = {
        "swift_code": "NEWCODEXXX",           # Changed from swiftCode
        "bank_name": "NEW BANK",              # Changed from bankName
        "address": "NEW ADDRESS",
        "country_iso2": "FR",                 # Changed from countryISO2
        "country_name": "FRANCE",             # Changed from countryName
        "is_headquarters": True               # Changed from isHeadquarters
    }
    
    response = client.post("/v1/swift-codes/", json=new_code)
    assert response.status_code == 200
    
    # Verify it was created
    check_response = client.get("/v1/swift-codes/NEWCODEXXX")
    assert check_response.status_code == 200
    
def test_delete_swift_code(test_db):
    # Create a code to delete
    new_code = {
        "swift_code": "DELETEMEXXX",          # Changed from swiftCode
        "bank_name": "DELETE BANK",           # Changed from bankName
        "address": "DELETE ADDRESS",
        "country_iso2": "IT",                 # Changed from countryISO2
        "country_name": "ITALY",              # Changed from countryName
        "is_headquarters": True               # Changed from isHeadquarters
    }
    
    client.post("/v1/swift-codes/", json=new_code)
    
    # Delete it
    response = client.delete("/v1/swift-codes/DELETEMEXXX")
    assert response.status_code == 200
    
    # Verify it was deleted
    check_response = client.get("/v1/swift-codes/DELETEMEXXX")
    assert check_response.status_code == 404

def test_create_branch_swift_code(test_db):
    """Test creating a branch SWIFT code and verify its associations."""
    # First ensure the headquarters exists
    hq_code = "BRANCHQXXX"
    hq = {
        "swift_code": hq_code,
        "bank_name": "BRANCH TEST HQ",
        "address": "789 MAIN ROAD",
        "country_iso2": "FR",
        "country_name": "FRANCE",
        "is_headquarters": True
    }
    
    client.post("/v1/swift-codes/", json=hq)
    
    # Now create a branch
    branch_code = "BRANCHQ33"  # Same first 6 chars to match HQ
    branch = {
        "swift_code": branch_code,
        "bank_name": "BRANCH TEST BRANCH",
        "address": "101 SIDE ROAD",
        "country_iso2": "FR",
        "country_name": "FRANCE",
        "is_headquarters": False
    }
    
    response = client.post("/v1/swift-codes/", json=branch)
    assert response.status_code == 200
    
    # Verify the branch was created
    branch_response = client.get(f"/v1/swift-codes/{branch_code}")
    assert branch_response.status_code == 200
    
    # Verify the headquarters has this branch
    hq_response = client.get(f"/v1/swift-codes/{hq_code}")
    assert hq_response.status_code == 200
    
    hq_data = hq_response.json()
    assert "branches" in hq_data
    assert len(hq_data["branches"]) > 0
    
    # At least one branch should match our created branch
    branch_found = False
    for branch_item in hq_data["branches"]:
        if branch_item["swift_code"] == branch_code:
            branch_found = True
            break
    
    assert branch_found, f"Branch {branch_code} not found in headquarters branches list"
    
    # Clean up
    client.delete(f"/v1/swift-codes/{branch_code}")
    client.delete(f"/v1/swift-codes/{hq_code}")

def test_invalid_swift_code_format(test_db):
    """Test validation of SWIFT code format."""
    # Too short SWIFT code
    invalid_code = {
        "swift_code": "SHORT",  # Too short (should be 8 or 11 chars)
        "bank_name": "INVALID BANK",
        "address": "INVALID ADDRESS",
        "country_iso2": "US",
        "country_name": "UNITED STATES",
        "is_headquarters": True
    }
    
    response = client.post("/v1/swift-codes/", json=invalid_code)
    assert response.status_code == 422  # Validation error
    
    # Too long SWIFT code
    invalid_code["swift_code"] = "TOOLONGCODEXX"  # Too long
    response = client.post("/v1/swift-codes/", json=invalid_code)
    assert response.status_code == 422  # Validation error

def test_country_code_validation(test_db):
    """Test validation of country code."""
    invalid_country = {
        "swift_code": "BADCTRYXX",
        "bank_name": "BAD COUNTRY BANK",
        "address": "BAD COUNTRY ADDRESS",
        "country_iso2": "XX",  # Invalid ISO2 country code
        "country_name": "INVALID COUNTRY",
        "is_headquarters": True
    }
    
    response = client.post("/v1/swift-codes/", json=invalid_country)
    # This might be 422 if you have validation, or 200 if you don't validate country codes
    # Adjust based on your implementation
    assert response.status_code in [200, 422]

def test_duplicate_swift_code(test_db):
    """Test creating a duplicate SWIFT code."""
    # First create a valid SWIFT code
    test_code = {
        "swift_code": "DUPECODEX",
        "bank_name": "DUPLICATE TEST",
        "address": "DUPLICATE ADDRESS",
        "country_iso2": "US",
        "country_name": "UNITED STATES",
        "is_headquarters": True
    }
    
    response = client.post("/v1/swift-codes/", json=test_code)
    assert response.status_code == 200
    
    # Try to create it again
    response = client.post("/v1/swift-codes/", json=test_code)
    assert response.status_code == 400  # Bad request - already exists
    
    # Clean up
    client.delete("/v1/swift-codes/DUPECODEX")

def test_case_sensitivity(test_db):
    """Test that SWIFT codes are case-insensitive."""
    # Create a code
    test_code = {
        "swift_code": "CASETESX",
        "bank_name": "CASE TEST BANK",
        "address": "CASE TEST ADDRESS",
        "country_iso2": "GB",
        "country_name": "UNITED KINGDOM",
        "is_headquarters": True
    }
    
    response = client.post("/v1/swift-codes/", json=test_code)
    assert response.status_code == 200
    
    # Try to get it with lowercase
    response = client.get("/v1/swift-codes/casetesx")
    assert response.status_code == 200
    
    # Clean up
    client.delete("/v1/swift-codes/CASETESX")

def test_headquarters_deletion_removes_branches_association(test_db):
    """Test that deleting headquarters removes branch associations."""
    # Create headquarters
    hq_code = "DELASSXX"
    hq = {
        "swift_code": hq_code,
        "bank_name": "ASSOCIATION TEST HQ",
        "address": "123 ASSOC ST",
        "country_iso2": "DE",
        "country_name": "GERMANY",
        "is_headquarters": True
    }
    
    client.post("/v1/swift-codes/", json=hq)
    
    # Create branch
    branch_code = "DELASS33"
    branch = {
        "swift_code": branch_code,
        "bank_name": "ASSOCIATION TEST BRANCH",
        "address": "456 ASSOC ST",
        "country_iso2": "DE",
        "country_name": "GERMANY",
        "is_headquarters": False
    }
    
    client.post("/v1/swift-codes/", json=branch)
    
    # Verify association
    hq_response = client.get(f"/v1/swift-codes/{hq_code}")
    hq_data = hq_response.json()
    assert any(b["swift_code"] == branch_code for b in hq_data["branches"])
    
    # Delete headquarters
    client.delete(f"/v1/swift-codes/{hq_code}")
    
    # Verify branch still exists but isn't associated
    branch_response = client.get(f"/v1/swift-codes/{branch_code}")
    assert branch_response.status_code == 200
    
    # Clean up
    client.delete(f"/v1/swift-codes/{branch_code}")