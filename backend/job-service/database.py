"""
Database configuration and session management for job service.
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
    "postgresql://jobservice:jobservice123@jobdb-postgres:5432/jobdb"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency injection for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from models import Job, JobApplication
    from sqlalchemy import text

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

    # Run migration to add new columns to existing tables
    try:
        with engine.begin() as conn:
            # Check if employee_username column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'job_applications'
                AND column_name = 'employee_username'
            """))

            if not result.fetchone():
                print("Running migration to add employee profile columns...")

                # Add new columns one by one
                conn.execute(text("""
                    ALTER TABLE job_applications
                    ADD COLUMN IF NOT EXISTS employee_username VARCHAR(255)
                """))

                conn.execute(text("""
                    ALTER TABLE job_applications
                    ADD COLUMN IF NOT EXISTS employee_email VARCHAR(255)
                """))

                conn.execute(text("""
                    ALTER TABLE job_applications
                    ADD COLUMN IF NOT EXISTS employee_phone VARCHAR(50)
                """))

                conn.execute(text("""
                    ALTER TABLE job_applications
                    ADD COLUMN IF NOT EXISTS employee_description TEXT
                """))

                print("✅ Migration completed successfully!")
            else:
                print("✅ Database schema is up to date")
    except Exception as e:
        print(f"⚠️ Warning during migration: {e}")
