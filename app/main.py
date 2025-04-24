import os
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.database import getDB, createTables
from app.utils.parser import SwiftCodeParser
from app.services.SWIFTService import SwiftCodeService

@asynccontextmanager
async def lifespan(app:FastAPI):
    createTables()

    db = next(getDB())

    from app.models import SwiftCode
    count = db.query(SwiftCode).count()

    if count == 0:
        # Add logging to debug data loading
        dataPath = os.environ.get("SWIFT_DATA_PATH", "data/swiftCodes.xlsx")
        logging.info(f"Checking for SWIFT data at: {dataPath}")

        if os.path.exists(dataPath):
            logging.info(f"Loading SWIFT data from: {dataPath}")
            parser = SwiftCodeParser(dataPath)
            swiftData = parser.parse()
            
            logging.info(f"Parsed {len(swiftData)} SWIFT codes")
            SwiftCodeService.bulkCreateSwiftCodes(db, swiftData)
            logging.info(f"Loaded {len(swiftData)} SWIFT codes into the database.")
        else:
            logging.warning(f"WARNING: Swift data file not found at {dataPath}. Absolute path: {os.path.abspath(dataPath)}")

    yield

app = FastAPI(
    title="SWIFT Code API",
    description="API for managing SWIFT codes and their associations.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
def healthCheck():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
