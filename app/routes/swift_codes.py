from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import DatabaseManager
from app.services.swift_service import SwiftCodeService
from pydantic import BaseModel
from app.controlers.swift_controllers import SwiftCodeController
from pydantic import validator

router = APIRouter(prefix="/v1/swift-codes", tags=["SWIFT Codes"])

class SwiftCodeBase(BaseModel):
    swift_code: str
    bank_name: str
    address: str
    country_iso2: str
    country_name: str
    is_headquarters: bool

    @validator('swift_code')
    def validate_swift_code(cls, v):
        try:
            SwiftCodeController.validate_swift_code(v)
        except ValueError as e:
            raise ValueError(str(e))
        return v.upper()
    
    @validator('country_iso2')
    def validate_country_iso2(cls, v):
        if len(v) != 2:
            raise ValueError("Country ISO2 code must be exactly 2 characters")
        return v.upper()

class SwiftCodeResponse(SwiftCodeBase):
    pass

class BranchResponse(SwiftCodeBase):
    pass

class SwiftCodeWithBranches(SwiftCodeResponse):
    branches: List[BranchResponse] = []

class CountrySwiftCodes(BaseModel):
    country_iso2: str
    country_name: str
    swift_codes: List[SwiftCodeResponse]

class MessageResponse(BaseModel):
    message: str

@router.get("/country/{country_iso2}", response_model=CountrySwiftCodes)
def get_country_swift_codes(country_iso2: str, db: Session = Depends(DatabaseManager.get_db)):
    result = SwiftCodeService.get_country_swift_code(db, country_iso2)

    return result

@router.get("/{swift_code}", response_model=SwiftCodeWithBranches)  
def get_swift_code(swift_code: str, db: Session = Depends(DatabaseManager.get_db)):
    result = SwiftCodeService.get_swift_code(db, swift_code)

    if not result:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
    
    if 'branches' not in result:
        result['branches'] = []
        
    return result

@router.post("/", response_model=MessageResponse)
def create_swift_code(swift_code: SwiftCodeBase, db: Session = Depends(DatabaseManager.get_db)):
    
    try:
        SwiftCodeService.create_swift_code(db, swift_code.model_dump())
        return {"message": f"SWIFT code {swift_code.swift_code} created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/{swift_code}", response_model=MessageResponse)
def delete_swift_code(swift_code: str, db: Session = Depends(DatabaseManager.get_db)):
    success = SwiftCodeService.delete_swift_code(db, swift_code)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
    
    return {"message": f"SWIFT code {swift_code} deleted successfully"}
