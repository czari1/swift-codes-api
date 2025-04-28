import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

class DatabaseManager:
    """
    Encapsulates database engine, session factory, and metadata management.
    """
    # Match environment variable with docker-compose
    database_path = os.environ.get("DATABASE_PATH", "./swift_codes.db")
    database_url = f"sqlite:///{database_path}"

    # Engine and session factory
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Base class for declarative models
    Base = declarative_base()

    @classmethod
    def create_tables(cls):
        """
        Create all tables defined on the Base metadata.
        """
        cls.Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def get_db(cls):
        """
        Dependency generator that provides a database session and ensures it is closed
        after use.
        Yields:
            Session: an SQLAlchemy session.
        """
        db = cls.SessionLocal()
        try:
            yield db
        finally:
            db.close()