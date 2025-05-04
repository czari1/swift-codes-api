from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.swift_code import SwiftCode
from app.models.branch_association import BranchAssociation

import uuid
import logging


class SwiftCodeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_swift_code(self, swift_code):
        swift_code = swift_code.upper()

        print(f"Fetching SWIFT code: {swift_code}")
        
        entry = self.db.query(SwiftCode).filter(SwiftCode.swift_code == swift_code).first()

        print(f"Entry: {entry}")

        if not entry:
            return None
        
        result = {
            'swift_code': entry.swift_code,
            'bank_name': entry.bank_name,
            'address': entry.address,
            'country_iso2': entry.country_iso2,
            'country_name': entry.country_name,
            'is_headquarters': entry.is_headquarters,
            'branches': [] 
        }

        if entry.is_headquarters:
            associations = self.db.query(BranchAssociation).filter(
                BranchAssociation.headquarter_swift == swift_code
            ).all()

            branches = []

            for assoc in associations:
                branch = self.db.query(SwiftCode).filter(
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

    def get_country_swift_codes(self, country_iso2):
        country_iso2 = country_iso2.upper()
        entries = self.db.query(SwiftCode).filter(
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

    def create_swift_code(self, swift_data):
        swift_code = swift_data['swift_code'].upper()
        
        existing = self.db.query(SwiftCode).filter(SwiftCode.swift_code == swift_code).first()
        if existing:
            raise ValueError(f"Swift code {swift_code} already exists.")
        
        new_swift_code = SwiftCode(
            swift_code=swift_code,
            bank_name=swift_data['bank_name'],
            address=swift_data['address'],
            country_iso2=swift_data['country_iso2'].upper(),
            country_name=swift_data['country_name'].upper(),
            is_headquarters=swift_data['is_headquarters']
        )
        
        self.db.add(new_swift_code)
        self.db.commit()
        self.db.refresh(new_swift_code)
        
        if not swift_data['is_headquarters']:
            hq_code = swift_code[:6] + 'XXX'
                
            hq = self.db.query(SwiftCode).filter(SwiftCode.swift_code == hq_code).first()
            
            if hq:

                association = BranchAssociation(
                    id=str(uuid.uuid4()),
                    headquarter_swift=hq_code,
                    branch_swift=swift_code
                )
                self.db.add(association)
                self.db.commit()
                logging.info(f"Created branch association: {swift_code} -> {hq_code}")
            else:
                logging.warning(f"Could not find headquarters {hq_code} for branch {swift_code}")
        
        return new_swift_code


    def bulk_create_swift_codes(self, swift_code_models, branch_hq_map, associations) -> None:
        

        self.db.add_all(swift_code_models)
        self.db.flush()
        

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
        
        if associations:
            self.db.add_all(associations)
        
        self.db.commit()


    def delete_swift_code(self, swift_code_id) -> bool:
        entry = self.db.query(SwiftCode).filter(
            SwiftCode.swift_code == swift_code_id).first()
        
        if not entry:
            return False
        
        if entry.is_headquarters:
            self.db.query(BranchAssociation).filter(
                BranchAssociation.headquarter_swift == swift_code_id
            ).delete()
        else:
            self.db.query(BranchAssociation).filter(
                BranchAssociation.branch_swift == swift_code_id
            ).delete()

        self.db.delete(entry)
        self.db.commit()

        return True
    
    def add_many_swift_codes(self, swift_code_models: List[Dict[str, Any]]) -> None:
        self.db.add_all(swift_code_models)
        self.db.flush()
        self.db.commit()

    def add_many_associations(self, associations: List[Dict[str, Any]]) -> None:
        self.db.add_all(associations)
        self.db.flush()
        self.db.commit()

