from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.swift_code import SwiftCode
from app.models.branch_association import BranchAssociation
import uuid

class SwiftCodeService:
    @staticmethod
    def create_swift_code(db: Session, swift_data: Dict[str, Any]) -> SwiftCode:
        existing = db.query(SwiftCode).filter(SwiftCode.swift_code == swift_data['swift_code']).first()

        if existing:
            raise ValueError(f"Swift code {swift_data['swift_code']} already exists.")
        
        swift_code = SwiftCode(
            swift_code=swift_data['swift_code'],
            bank_name=swift_data['bank_name'],
            address=swift_data['address'],
            country_iso2=swift_data['country_iso2'],
            country_name=swift_data['country_name'],
            is_headquarters=swift_data['is_headquarters']
        )

        db.add(swift_code)
        db.commit()
        db.refresh(swift_code)

        if not swift_data['is_headquarters']:
            potential_hq = swift_data['swift_code'][:-3] + 'XXX'
            hq = db.query(SwiftCode).filter(SwiftCode.swift_code == potential_hq).first()

            if hq:
                association = BranchAssociation(
                    id=str(uuid.uuid4()),
                    headquarter_swift=hq.swift_code,
                    branch_swift=swift_data['swift_code']
                )
                db.add(association)
                db.commit()
        
        return swift_code
    
    @staticmethod
    def bulk_create_swift_codes(db: Session, swift_codes: List[Dict[str, Any]]) -> None:
        swift_code_models = []
        
        for data in swift_codes:
            swift_code_model = SwiftCode(
                swift_code=data['swift_code'],
                bank_name=data['bank_name'],
                address=data['address'],
                country_iso2=data['country_iso2'],
                country_name=data['country_name'],
                is_headquarters=data['is_headquarters']
            )
            swift_code_models.append(swift_code_model)
        
        db.add_all(swift_code_models)
        
        for data in swift_codes:
            if not data['is_headquarters']:
                potential_hq = data['swift_code'][:-3] + 'XXX'
                hq = db.query(SwiftCode).filter(SwiftCode.swift_code == potential_hq).first()
                
                if hq:
                    association = BranchAssociation(
                        id=str(uuid.uuid4()),
                        headquarter_swift=hq.swift_code,
                        branch_swift=data['swift_code']
                    )
                    db.add(association)
        
        db.commit()
    
    @staticmethod
    def get_swift_code(db: Session, swift_code: str) -> Optional[Dict[str, Any]]:
        # Convert to uppercase for case-insensitive lookup
        swift_code = swift_code.upper()
        
        entry = db.query(SwiftCode).filter(SwiftCode.swift_code == swift_code).first()

        if not entry:
            return None
        
        result = {
            'swift_code': entry.swift_code,
            'bank_name': entry.bank_name,
            'address': entry.address,
            'country_iso2': entry.country_iso2,
            'country_name': entry.country_name,
            'is_headquarters': entry.is_headquarters,
            'branches': []  # Always initialize with empty list
        }

        if entry.is_headquarters:
            associations = db.query(BranchAssociation).filter(
                BranchAssociation.headquarter_swift == swift_code
            ).all()

            branches = []

            for assoc in associations:
                branch = db.query(SwiftCode).filter(
                    SwiftCode.swift_code == assoc.branch_swift).first()
                
                if branch:
                    branches.append({
                        'swift_code': branch.swift_code,
                        'bank_name': branch.bank_name,
                        'address': branch.address,
                        'country_iso2': branch.country_iso2,
                        'country_name': branch.country_name,
                        'is_headquarters': branch.is_headquarters
                    })
            
            result['branches'] = branches

        return result
    
    @staticmethod
    def get_country_swift_code(db: Session, country_iso2: str) -> Dict[str, Any]:
        country_iso2 = country_iso2.upper()
        entries = db.query(SwiftCode).filter(
            SwiftCode.country_iso2 == country_iso2).all()
        
        if not entries:
            return {
                'country_iso2': country_iso2,
                'country_name': "",
                'swift_codes': []
            }
        
        country_name = entries[0].country_name

        swift_codes = []

        for entry in entries:
            swift_codes.append({
                'swift_code': entry.swift_code,
                'bank_name': entry.bank_name,
                'address': entry.address,
                'country_iso2': entry.country_iso2,
                'country_name': entry.country_name,
                'is_headquarters': entry.is_headquarters
            })
        
        return {
            'country_iso2': country_iso2,
            'country_name': country_name,
            'swift_codes': swift_codes
        }
        
    @staticmethod
    def delete_swift_code(db: Session, swift_code: str) -> bool:
        entry = db.query(SwiftCode).filter(
            SwiftCode.swift_code == swift_code).first()
        
        if not entry:
            return False
        
        if entry.is_headquarters:
            db.query(BranchAssociation).filter(
                BranchAssociation.headquarter_swift == swift_code
            ).delete()

        db.delete(entry)
        db.commit()
        return True