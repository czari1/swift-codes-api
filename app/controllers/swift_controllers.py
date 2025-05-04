from typing import Dict, Any, List
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
from app.models.swift_code import SwiftCode
from app.models.types import SwiftCodeBase
from app.services.swift_service import SwiftCodeService
from fastapi import APIRouter, Depends, HTTPException
from app.database import DatabaseManager
import re

SWIFT_CODE_PATTERN = re.compile(r'^[A-Z0-9]{4,11}(?:XXX)?$')


class SwiftCodeController:
    def __init__(self, swift_service: SwiftCodeService):
        self.swift_service = swift_service

    def validate_swift_code(self, swift_code: str) -> bool:
        if not SWIFT_CODE_PATTERN.match(swift_code):
            raise ValueError(f"Invalid SWIFT code format: {swift_code}")
        return True
    
    @staticmethod
    def is_headquarters(swift_code: str) -> bool:
        """Check if a SWIFT code represents a headquarters (ends with XXX)."""
        return swift_code.endswith('XXX')
    
    async def create_swift_code(self, swift_data: SwiftCodeBase):
        print(f"Creating SWIFT code: {swift_data}")
        swift_code = swift_data.swift_code.upper()
        
        # Validate the SWIFT code format
        try:
            self.validate_swift_code(swift_code)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        try:
            # First check if the code already exists
            existing = await self.swift_service.get_swift_code(swift_code)
            if existing:
                raise HTTPException(status_code=409, detail=f"Swift code {swift_code} already exists.")
            
            # Create the new SWIFT code
            await self.swift_service.create_swift_code(swift_data.model_dump())
            return {"message": f"SWIFT code {swift_code} created successfully"}
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle any other errors
            raise HTTPException(status_code=500, detail=f"Error creating SWIFT code: {str(e)}")


    async def get_swift_code(self, swift_code: str):
        print(f"Getting SWIFT code from controller: {swift_code}")
        result = await self.swift_service.get_swift_code(swift_code)

        if not result:
            raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")

        return result
    
    async def get_country_swift_codes(self, country_iso2: str):
        result = await self.swift_service.get_country_swift_codes(country_iso2)

        if not result:
            raise HTTPException(status_code=404, detail=f"No SWIFT codes found for country {country_iso2}")
        return result
    
    # async def create_swift_code(self, swift_code: SwiftCodeBase):
    #     try:
    #         await self.swift_service.create_swift_code(swift_code.model_dump())

    #         return {"message": f"SWIFT code {swift_code.swift_code} created successfully"}
    #     except ValueError as e:
    #         raise HTTPException(status_code=400, detail=str(e))
    
    async def delete_swift_code(self, swift_code: str):
        if await self.swift_service.delete_swift_code(swift_code):
            return {"message": f"SWIFT code {swift_code} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
        
