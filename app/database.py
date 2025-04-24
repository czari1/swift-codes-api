import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Match environment variable with docker-compose
DatabasePath = os.environ.get("DATABASE_PATH", "./swift_codes.db")
DatabaseURL = f"sqlite:///{DatabasePath}"

engine = create_engine(DatabaseURL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def createTables():
    Base.metadata.create_all(bind=engine)

def getDB():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()