from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SwiftCode(Base):
    __tablename__ = "swiftCodes"

    swiftCode = Column(String, primary_key=True, index=True)
    bankName = Column(String, nullable=False)
    address = Column(String, nullable=False)
    countryISO2 = Column(String(2), nullable=False, index=True)
    countryName = Column(String, nullable=False)
    isHeadquarters = Column(Boolean, default=False)

    branches = relationship(
        "BranchAssociation",
        back_populates="headquarter",
        foreign_keys="BranchAssociation.headquarterSwift",
        cascade="all, delete-orphan"
    )

class BranchAssociation(Base):
    __tablename__ = "branchAssociations"

    id = Column(String, primary_key=True)
    headquarterSwift = Column(String, ForeignKey("swiftCodes.swiftCode"))
    branchSwift = Column(String, ForeignKey("swiftCodes.swiftCode"))

    headquarter = relationship(
        "SwiftCode",
        back_populates="branches",
        foreign_keys=[headquarterSwift]
    )