import os
import logging
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.swift_codes import SwiftCodesRoutes
from app.database import DatabaseManager
from app.utils.parser import SwiftCodeParser
from app.repositories.swift_code_repository import SwiftCodeRepository
from app.services.swift_service import SwiftCodeService
from app.controllers.swift_controllers import SwiftCodeController
from app.models.swift_code import SwiftCode

swift_code_repository = SwiftCodeRepository(next(DatabaseManager.get_db()))
swift_code_service = SwiftCodeService(swift_code_repository)
swift_code_controller = SwiftCodeController(swift_code_service)
swift_code_routes = SwiftCodesRoutes(swift_code_controller).router

@asynccontextmanager
async def lifespan(app:FastAPI):
    DatabaseManager.create_tables()

    db = next(DatabaseManager.get_db())
    count = db.query(SwiftCode).count()

    if count == 0:
        data_path = os.environ.get("SWIFT_DATA_PATH", "data/swiftCodes.xlsx")
        base_path, ext = os.path.splitext(data_path)


        print("Checking for SWIFT data file...")
        
        if not os.path.exists(data_path) and os.path.exists(f"{base_path}.csv"):
            data_path = f"{base_path}.csv"
            logging.info(f"Excel file not found, using CSV file: {data_path}")
        
        if not os.path.exists(data_path):
            alternatives = [
                "data/swiftCodes.csv", 
                "data/swift_data.xlsx", 
                "data/swift_data.csv",
                "data/swift_codes.xlsx",
                "data/swift_codes.csv"
            ]
            
            for alt_path in alternatives:
                if os.path.exists(alt_path) and alt_path != data_path:
                    data_path = alt_path
                    logging.info(f"Using alternative data file: {data_path}")
                    break
        
        logging.info(f"Checking for SWIFT data at: {data_path}")

        if os.path.exists(data_path):
            logging.info(f"Loading SWIFT data from: {data_path}")
            parser = SwiftCodeParser(data_path)
            
            swift_data = parser.parse_files()
            
            logging.info(f"Parsed {len(swift_data)} SWIFT codes")
            
            swift_code_repository.bulk_create_swift_codes(swift_data)
            
            logging.info(f"Loaded {len(swift_data)} SWIFT codes into the database.")
        else:
            logging.warning(f"WARNING: Swift data file not found at {data_path} or any alternative locations. Absolute path: {os.path.abspath(data_path)}")

    yield

app = FastAPI(
    title="SWIFT Code API",
    description="API for managing SWIFT codes and their associations.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(swift_code_routes)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
