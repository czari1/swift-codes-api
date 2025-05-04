from typing import Dict, Any, Optional
from app.repositories.swift_code_repository import SwiftCodeRepository


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
    
    async def add_many_swift_codes(self, swift_codes: list[Dict[str, Any]]):
        many_swift_codes = self.swift_code_repository.add_many_swift_codes(swift_codes)

        return many_swift_codes
    
    async def add_many_associations(self, associations: list[Dict[str, Any]]):
        many_associations = self.swift_code_repository.add_many_associations(associations)

        return many_associations
    

