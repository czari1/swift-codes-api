from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import DatabaseManager

class BranchAssociation(DatabaseManager.Base):
    __tablename__ = "branch_associations"

    id = Column(String, primary_key=True)
    headquarter_swift = Column(String, ForeignKey("swift_codes.swift_code"))
    branch_swift = Column(String, ForeignKey("swift_codes.swift_code"))

    headquarter = relationship(
        "SwiftCode",
        back_populates="branches",
        foreign_keys=[headquarter_swift]
    )