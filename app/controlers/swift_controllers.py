from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.swift_code import SwiftCode
import re

SWIFT_CODE_PATTERN = re.compile(r'^[A-Z0-9]{4,11}(?:XXX)?$')

class SwiftCodeController:
    @staticmethod
    def validate_swift_code(swift_code: str) -> bool:
        
        if not SWIFT_CODE_PATTERN.match(swift_code):
            raise ValueError(f"Invalid SWIFT code format: {swift_code}")
        return True
    
    @staticmethod
    def is_headquarters(swift_code: str) -> bool:
        """Check if a SWIFT code represents a headquarters (ends with XXX)."""
        return swift_code.endswith('XXX')
    
    def create_swift_code(swift_service, db: Session, swift_data: Dict[str, Any]) -> SwiftCode:
        swift_code = swift_data['swift_code'].upper()
        SwiftCodeController.validate_swift_code(swift_code)
        
        existing = db.query(SwiftCode).filter(SwiftCode.swift_code == swift_data['swift_code']).first()

        if existing:
            raise ValueError(f"Swift code {swift_data['swift_code']} already exists.")

