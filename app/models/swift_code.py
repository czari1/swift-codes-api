from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import DatabaseManager
from pydantic import BaseModel, validator
from typing import List, Dict, Any

# class SwiftCodeBase(BaseModel):
#     swift_code: str
#     bank_name: str
#     address: str
#     country_iso2: str
#     country_name: str
#     is_headquarters: bool


    # @validator('swift_code')
    # def validate_swift_code(cls, v):
    #     try:
    #         SwiftCodeController.validate_swift_code(v)
    #     except ValueError as e:
    #         raise ValueError(str(e))
    #     return v.upper()
    
    # @validator('country_iso2')
    # def validate_country_iso2(cls, v):
    #     if len(v) != 2:
    #         raise ValueError("Country ISO2 code must be exactly 2 characters")
    #     return v.upper()

# class SwiftCodeResponse(SwiftCodeBase):
#     pass

# class BranchResponse(SwiftCodeBase):
#     pass

# class SwiftCodeWithBranchesResponse(SwiftCodeResponse):
#     branches: List[BranchResponse] = []

# class CountrySwiftCodesResponse(BaseModel):
#     country_iso2: str
#     country_name: str
#     swift_codes: List[SwiftCodeResponse]

class SwiftCode(DatabaseManager.Base):
    __tablename__ = "swift_codes"

    swift_code = Column(String, primary_key=True, index=True)
    bank_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    country_iso2 = Column(String(2), nullable=False, index=True)
    country_name = Column(String, nullable=False)
    is_headquarters = Column(Boolean, default=False)

    branches = relationship(
        "BranchAssociation",
        back_populates="headquarter",
        foreign_keys="BranchAssociation.headquarter_swift",
        cascade="all, delete-orphan"
    )
