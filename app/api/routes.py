from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import getDB
from app.services.SWIFTService import SwiftCodeService
from pydantic import BaseModel

# Create the router
router = APIRouter(prefix="/v1/swift-codes", tags=["SWIFT Codes"])

# Define your model classes
class SwiftCodeBase(BaseModel):
    swiftCode: str
    bankName: str
    address: str
    countryISO2: str
    countryName: str
    isHeadquarters: bool

class SwiftCodeResponse(SwiftCodeBase):
    pass

class BranchResponse(SwiftCodeBase):
    pass

class SwiftCodeWithBranches(SwiftCodeResponse):
    branches: List[BranchResponse] = []

class CountrySwiftCodes(BaseModel):
    countryISO2: str
    countryName: str
    swiftCodes: List[SwiftCodeResponse]

class MessageResponse(BaseModel):
    message: str

# Define your routes
@router.get("/country/{country_iso2}", response_model=CountrySwiftCodes)
def get_country_swift_codes(country_iso2: str, db: Session = Depends(getDB)):
    result = SwiftCodeService.getCountrySwiftCode(db, country_iso2)
    return result

@router.get("/{swift_code}", response_model=None)  # Remove response model validation temporarily
def get_swift_code(swift_code: str, db: Session = Depends(getDB)):
    result = SwiftCodeService.getSwiftCode(db, swift_code)
    if not result:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
    
    # Explicitly ensure 'branches' is included
    if 'branches' not in result:
        result['branches'] = []
        
    return result

@router.post("/", response_model=MessageResponse)
def create_swift_code(swift_code: SwiftCodeBase, db: Session = Depends(getDB)):
    try:
        # Change from .dict() to .model_dump() for Pydantic V2
        SwiftCodeService.createSwiftCode(db, swift_code.model_dump())
        return {"message": f"SWIFT code {swift_code.swiftCode} created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{swift_code}", response_model=MessageResponse)
def delete_swift_code(swift_code: str, db: Session = Depends(getDB)):
    success = SwiftCodeService.deleteSwiftCode(db, swift_code)
    if not success:
        raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
    return {"message": f"SWIFT code {swift_code} deleted successfully"}
