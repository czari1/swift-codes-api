from typing import List
from pydantic import BaseModel


class SwiftCodeBase(BaseModel):
    swift_code: str
    bank_name: str
    address: str
    country_iso2: str
    country_name: str
    is_headquarters: bool

class SwiftCodeResponse(SwiftCodeBase):
    pass

class BranchResponse(SwiftCodeBase):
    pass

class SwiftCodeWithBranchesResponse(SwiftCodeResponse):
    branches: List[BranchResponse] = []

class CountrySwiftCodesResponse(BaseModel):
    country_iso2: str
    country_name: str
    swift_codes: List[SwiftCodeResponse]

