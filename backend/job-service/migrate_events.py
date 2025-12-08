"""
Database migration script to create events table for event sourcing.
Run this script to add the events table to the job service database.
"""
from database import engine, Base
from models import Event, Job, JobApplication
import sys


def create_events_table():
    """Create the events table in the database."""
    try:
        print("Creating events table...")

        # Import all models to ensure they are registered with Base
        # This is important so that SQLAlchemy knows about all tables

        # Create only the events table
        Event.__table__.create(engine, checkfirst=True)

        print("✅ Events table created successfully!")
        print(f"Table: {Event.__tablename__}")
        print(f"Columns: {', '.join([col.name for col in Event.__table__.columns])}")

        return True

    except Exception as e:
        print(f"❌ Failed to create events table: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = create_events_table()
    sys.exit(0 if success else 1)
