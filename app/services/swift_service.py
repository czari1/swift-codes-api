from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.branch_association import BranchAssociation
from app.repositories.swift_code_repository import SwiftCodeRepository
import uuid
import logging

class SwiftCodeService:
    def __init__(self, swift_code_repository: SwiftCodeRepository):
        self.swift_code_repository = swift_code_repository

    async def create_swift_code(self, swift_data: Dict[str, Any]):
        new_swift_code = self.swift_code_repository.create_swift_code(swift_data)

        return new_swift_code
    
    
    async def get_swift_code(self, swift_code: str) -> Optional[Dict[str, Any]]:
        swift_code = self.swift_code_repository.get_swift_code(swift_code)
    
        return swift_code


    async def get_country_swift_codes(self, country_iso2: str) -> Dict[str, Any]:
        swift_codes_contries = self.swift_code_repository.get_country_swift_codes(country_iso2)
        
        return swift_codes_contries


    async def delete_swift_code(self, swift_code: str) -> bool:
        deleted_swift_code = self.swift_code_repository.delete_swift_code(swift_code)

        return deleted_swift_code

