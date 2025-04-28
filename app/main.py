import os
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.database import get_db, create_tables
from app.utils.parser import SwiftCodeParser
from app.services.swift_service import SwiftCodeService

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_tables()

    db = next(get_db())

    from app.models import SwiftCode
    count = db.query(SwiftCode).count()

    if count == 0:
        # Add logging to debug data loading
        data_path = os.environ.get("SWIFT_DATA_PATH", "data/swiftCodes.xlsx")
        logging.info(f"Checking for SWIFT data at: {data_path}")

        if os.path.exists(data_path):
            logging.info(f"Loading SWIFT data from: {data_path}")
            parser = SwiftCodeParser(data_path)
            swift_data = parser.parse()
            
            logging.info(f"Parsed {len(swift_data)} SWIFT codes")
            SwiftCodeService.bulk_create_swift_codes(db, swift_data)
            logging.info(f"Loaded {len(swift_data)} SWIFT codes into the database.")
        else:
            logging.warning(f"WARNING: Swift data file not found at {data_path}. Absolute path: {os.path.abspath(data_path)}")

    yield

app = FastAPI(
    title="SWIFT Code API",
    description="API for managing SWIFT codes and their associations.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
