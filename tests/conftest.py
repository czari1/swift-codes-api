import os
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database import DatabaseManager
from app.main import app
from app.models.swift_code import SwiftCode
from app.models.branch_association import BranchAssociation
from app.repositories.swift_code_repository import SwiftCodeRepository
from app.services.swift_service import SwiftCodeService
from app.controllers.swift_controllers import SwiftCodeController

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    SwiftCode.metadata.create_all(bind=engine)
    BranchAssociation.metadata.create_all(bind=engine)

    db = TestSessionLocal()
    yield db
    db.close()

@pytest.fixture
def swift_repository(test_db):
    return SwiftCodeRepository(test_db)

@pytest.fixture
def swift_service(swift_repository):
    return SwiftCodeService(swift_repository)

@pytest.fixture
def swift_controller(swift_service):
    return SwiftCodeController(swift_service)

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_swift_data():
    return [
        {
            "swift_code": "AAAAUSXXXXX",
            "bank_name": "Test Bank HQ",
            "address": "123 Main St, New York",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": True
        },
        {
            "swift_code": "AAAAUS33",
            "bank_name": "Test Bank Branch",
            "address": "456 Second St, Boston",
            "country_iso2": "US",
            "country_name": "UNITED STATES",
            "is_headquarters": False
        },
        {
            "swift_code": "BBBBGBXXXXX",
            "bank_name": "Euro Bank HQ",
            "address": "1 London Road",
            "country_iso2": "GB",
            "country_name": "UNITED KINGDOM",
            "is_headquarters": True
        }
    ]

@pytest.fixture
def create_test_excel():
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    
    file_path = os.path.join(fixture_dir, "test_swift_codes.xlsx")
    
    data = {
        "country_iso2_code": ["US", "US", "GB"],
        "swift_code": ["AAAAUSXXXXX", "AAAAUS33", "BBBBGBXXXXX"],
        "name": ["Test Bank HQ", "Test Bank Branch", "Euro Bank HQ"],
        "address": ["123 Main St, New York", "456 Second St, Boston", "1 London Road"],
        "country_name": ["United States", "United States", "United Kingdom"]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    
    return file_path

@pytest.fixture
def create_test_csv():
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    
    file_path = os.path.join(fixture_dir, "test_swift_codes.csv")
    
    data = {
        "country_iso2_code": ["US", "US", "GB"],
        "swift_code": ["AAAAUSXXXXX", "AAAAUS33", "BBBBGBXXXXX"],
        "name": ["Test Bank HQ", "Test Bank Branch", "Euro Bank HQ"],
        "address": ["123 Main St, New York", "456 Second St, Boston", "1 London Road"],
        "country_name": ["United States", "United States", "United Kingdom"]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    
    return file_path

@pytest.fixture
def invalid_test_excel():
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    
    file_path = os.path.join(fixture_dir, "invalid_swift_codes.xlsx")

    data = {
        "country_code": ["US", "GB"],
        "swift": ["AAAAUSXXXXX", "BBBBGBXXXXX"],
        "name": ["Test Bank", "Euro Bank"]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    
    return file_path