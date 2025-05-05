import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

def ensure_db_directory_exists():
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
    if not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    return db_dir

class DatabaseManager:
    db_dir = ensure_db_directory_exists()
    database_path = os.path.join(db_dir, "swift_codes.db")
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