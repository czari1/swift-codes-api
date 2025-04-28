from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.swift_service import SwiftCodeService
from pydantic import BaseModel

# Create the router
router = APIRouter(prefix="/v1/swift-codes", tags=["SWIFT Codes"])

# Define your model classes
class SwiftCodeBase(BaseModel):
    swift_code: str
    bank_name: str
    address: str
    country_iso2: str
    country_name: str
    is_headquarters: bool

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
def get_country_swift_codes(country_iso2: str, db: Session = Depends(get_db)):
    result = SwiftCodeService.get_country_swift_code(db, country_iso2)
    return result

@router.get("/{swift_code}", response_model=None)  # Remove response model validation temporarily
def get_swift_code(swift_code: str, db: Session = Depends(get_db)):
    result = SwiftCodeService.get_swift_code(db, swift_code)
    if not result:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
    
    # Explicitly ensure 'branches' is included
    if 'branches' not in result:
        result['branches'] = []
        
    return result

@router.post("/", response_model=MessageResponse)
def create_swift_code(swift_code: SwiftCodeBase, db: Session = Depends(get_db)):
    try:
        # Change from .dict() to .model_dump() for Pydantic V2
        SwiftCodeService.create_swift_code(db, swift_code.model_dump())
        return {"message": f"SWIFT code {swift_code.swift_code} created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{swift_code}", response_model=MessageResponse)
def delete_swift_code(swift_code: str, db: Session = Depends(get_db)):
    success = SwiftCodeService.delete_swift_code(db, swift_code)
    if not success:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
    return {"message": f"SWIFT code {swift_code} deleted successfully"}
