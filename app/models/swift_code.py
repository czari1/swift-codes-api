from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import DatabaseManager

class SwiftCode(DatabaseManager.Base):
    __tablename__ = "swift_codes"

    swift_code = Column(String, primary_key=True, index=True)
    bank_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    country_iso2 = Column(String(2), nullable=False, index=True)
    country_name = Column(String, nullable=False)
    is_headquarters = Column(Boolean, default=False)

    branches = relationship(
        "BranchAssociation",
        back_populates="headquarter",
        foreign_keys="BranchAssociation.headquarter_swift",
        cascade="all, delete-orphan"
    )
