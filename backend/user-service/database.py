"""
Database configuration and session management.
Single Responsibility: Handles only database connection setup.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://userservice:userservice123@userdb-postgres:5432/userdb"
)

print("=" * 60)
print(f"🔗 Connecting to database:")
print(f"   DATABASE_URL: {DATABASE_URL}")
print("=" * 60)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency injection for database session (generator for FastAPI-style dependency injection)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db_session():
    """Create a new database session for manual management."""
    return SessionLocal()


def init_db():
    """Initialize database tables."""
    from models import UserProfile
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
