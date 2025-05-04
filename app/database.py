import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

class DatabaseManager:
    database_path = os.environ.get("DATABASE_PATH", "./swift_codes.db")
    database_url = f"sqlite:///{database_path}"

    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

    @classmethod
    def create_tables(cls):

        cls.Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def get_db(cls):
        
        db = cls.SessionLocal()
        try:
            yield db
        finally:
            db.close()