from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import DatabaseManager
from app.services.swift_service import SwiftCodeService
from pydantic import BaseModel , validator
from app.controllers.swift_controllers import SwiftCodeController
from app.models.types import SwiftCodeBase, SwiftCodeWithBranchesResponse, CountrySwiftCodesResponse, SwiftCodeBase

class SwiftCodesRoutes:
    def __init__(self, swift_controller: SwiftCodeController):
        self.swift_controller = swift_controller

        # Create router instance here
        self.router = APIRouter(prefix="/v1/swift-codes", tags=["swift-codes"])
        
        # Define routes using the router instance
        self.router.add_api_route("/", self.create_swift_code, methods=["POST"])
        self.router.add_api_route("/{swift_code}", self.get_swift_code, methods=["GET"], response_model=SwiftCodeWithBranchesResponse)
        self.router.add_api_route("/{swift_code}", self.delete_swift_code, methods=["DELETE"])
        self.router.add_api_route("/country/{country_iso2}", self.get_country_swift_codes, methods=["GET"], response_model=CountrySwiftCodesResponse)
    
    async def get_swift_code(self, swift_code: str):
        print(f"Getting SWIFT code: {swift_code}")
        result = await self.swift_controller.get_swift_code(swift_code)
        
        return result
    
    async def get_country_swift_codes(self, country_iso2: str):
        result = await self.swift_controller.get_country_swift_codes(country_iso2)
        
        return result
    
    async def create_swift_code(self, swift_code: SwiftCodeBase):
        result = await self.swift_controller.create_swift_code(swift_code)
        
        return result
        
    
    async def delete_swift_code(self, swift_code: str):
        result = await self.swift_controller.delete_swift_code(swift_code)
        
        return result
