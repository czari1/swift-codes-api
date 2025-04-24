from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import SwiftCode, BranchAssociation
import uuid

class SwiftCodeService:
    @staticmethod
    def createSwiftCode(db: Session, swiftData: Dict[str, Any]) -> SwiftCode:
        existing = db.query(SwiftCode).filter(SwiftCode.swiftCode == swiftData['swiftCode']).first()

        if existing:
            raise ValueError(f"Swift code {swiftData['swiftCode']} already exists.")
        
        swiftCode = SwiftCode(
            swiftCode=swiftData['swiftCode'],
            bankName=swiftData['bankName'],
            address=swiftData['address'],
            countryISO2=swiftData['countryISO2'],
            countryName=swiftData['countryName'],
            isHeadquarters=swiftData['isHeadquarters']
        )

        db.add(swiftCode)
        db.commit()
        db.refresh(swiftCode)

        if not swiftData['isHeadquarters']:
            potentialHq = swiftData['swiftCode'][:-3] + 'XXX'
            hq = db.query(SwiftCode).filter(SwiftCode.swiftCode == potentialHq).first()

            if hq:
                association = BranchAssociation(
                    id=str(uuid.uuid4()),
                    headquarterSwift=hq.swiftCode,
                    branchSwift=swiftData['swiftCode']
                )
                db.add(association)
                db.commit()
        
        return swiftCode
    
    @staticmethod
    def bulkCreateSwiftCodes(db: Session, swiftCodes: List[Dict[str, Any]]) -> None:
        swiftCodeModels = []
        
        for data in swiftCodes:
            swiftCodeModel = SwiftCode(
                swiftCode=data['swiftCode'],
                bankName=data['bankName'],
                address=data['address'],
                countryISO2=data['countryISO2'],
                countryName=data['countryName'],
                isHeadquarters=data['isHeadquarters']
            )
            swiftCodeModels.append(swiftCodeModel)
        
        db.add_all(swiftCodeModels)
        
        for data in swiftCodes:
            if not data['isHeadquarters']:
                potentialHq = data['swiftCode'][:-3] + 'XXX'
                hq = db.query(SwiftCode).filter(SwiftCode.swiftCode == potentialHq).first()
                
                if hq:
                    association = BranchAssociation(
                        id=str(uuid.uuid4()),
                        headquarterSwift=hq.swiftCode,
                        branchSwift=data['swiftCode']
                    )
                    db.add(association)
        
        db.commit()
    
    @staticmethod
    def getSwiftCode(db: Session, swiftCode: str) -> Optional[Dict[str, Any]]:
        entry = db.query(SwiftCode).filter(SwiftCode.swiftCode == swiftCode).first()

        if not entry:
            return None
        
        result = {
            'swiftCode': entry.swiftCode,
            'bankName': entry.bankName,
            'address': entry.address,
            'countryISO2': entry.countryISO2,
            'countryName': entry.countryName,
            'isHeadquarters': entry.isHeadquarters,
            'branches': []  # Always initialize with empty list
        }

        if entry.isHeadquarters:
            associations = db.query(BranchAssociation).filter(
                BranchAssociation.headquarterSwift == swiftCode
            ).all()

            branches = []

            for assoc in associations:
                branch = db.query(SwiftCode).filter(
                    SwiftCode.swiftCode == assoc.branchSwift).first()
                
                if branch:
                    branches.append({
                        'swiftCode': branch.swiftCode,
                        'bankName': branch.bankName,
                        'address': branch.address,
                        'countryISO2': branch.countryISO2,
                        'countryName': branch.countryName,
                        'isHeadquarters': branch.isHeadquarters
                    })
            
            result['branches'] = branches

        return result
    
    @staticmethod
    def getCountrySwiftCode(db: Session, countryISO2: str) -> Dict[str, Any]:
        countryISO2 = countryISO2.upper()
        entries = db.query(SwiftCode).filter(
            SwiftCode.countryISO2 == countryISO2).all()
        
        if not entries:
            return {
                'countryISO2': countryISO2,
                'countryName': "",
                'swiftCodes': []
            }
        
        countryName = entries[0].countryName

        swiftCodes = []

        for entry in entries:
            swiftCodes.append({
                'swiftCode': entry.swiftCode,
                'bankName': entry.bankName,
                'address': entry.address,
                'countryISO2': entry.countryISO2,
                'countryName': entry.countryName,
                'isHeadquarters': entry.isHeadquarters
            })
        
        return {
            'countryISO2': countryISO2,
            'countryName': countryName,
            'swiftCodes': swiftCodes
        }
        
    @staticmethod
    def deleteSwiftCode(db: Session, swiftCode: str) -> bool:
        entry = db.query(SwiftCode).filter(
            SwiftCode.swiftCode == swiftCode).first()
        
        if not entry:
            return False
        
        if entry.isHeadquarters:
            db.query(BranchAssociation).filter(
                BranchAssociation.headquarterSwift == swiftCode
            ).delete()

        db.delete(entry)
        db.commit()
        return True