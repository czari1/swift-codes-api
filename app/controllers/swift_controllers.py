from app.models.types import SwiftCodeBase
from app.services.swift_service import SwiftCodeService
from fastapi import HTTPException
from app.models.swift_code import SwiftCode
from app.models.branch_association import BranchAssociation
import re
import uuid

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
        
        try:
            self.validate_swift_code(swift_code)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        try:
            existing = await self.swift_service.get_swift_code(swift_code)
            if existing:
                raise HTTPException(status_code=409, detail=f"Swift code {swift_code} already exists.")
            
            await self.swift_service.create_swift_code(swift_data.model_dump())
            return {"message": f"SWIFT code {swift_code} created successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
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
    
    async def delete_swift_code(self, swift_code: str):
        if await self.swift_service.delete_swift_code(swift_code):
            return {"message": f"SWIFT code {swift_code} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"SWIFT code {swift_code} not found")
        
    async def bulk_create_swift_codes(self, swift_codes: list[SwiftCodeBase]):
        swift_code_models = []
        associations = []
        branch_hq_map = {}
        
        for data in swift_codes:
            swift_code_str = data['swift_code'].upper()

            try:
                self.SwiftCodeController.validate_swift_code(swift_code_str)
            except ValueError:
                continue


            swift_code_model = SwiftCode(
                swift_code=data['swift_code'],
                bank_name=data['bank_name'],
                address=data['address'],
                country_iso2=data['country_iso2'],
                country_name=data['country_name'],
                is_headquarters=data['is_headquarters']
            )
            swift_code_models.append(swift_code_model)
        
            if not data['is_headquarters']:
                potential_hq = swift_code_str[:-3] + 'XXX'
                if potential_hq not in branch_hq_map:
                    branch_hq_map[potential_hq] = []
                branch_hq_map[potential_hq].append(swift_code_str)
        
        self.swift_service.add_many_swift_codes(swift_code_models)
    
        for hq_code, branch_codes in branch_hq_map.items():
            hq = self.db.query(SwiftCode).filter(SwiftCode.swift_code == hq_code).first()
            if hq:
                for branch_code in branch_codes:
                    association = BranchAssociation(
                        id=str(uuid.uuid4()),
                        headquarter_swift=hq_code,
                        branch_swift=branch_code
                    )
                    associations.append(association)
        
        self.swift_service.add_many_associations(associations)
    