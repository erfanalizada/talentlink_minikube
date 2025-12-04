"""
Database migration script to add employee profile columns to job_applications table.
Run this once to update the existing database schema.
"""
from sqlalchemy import text
from database import engine, init_db

def migrate():
    """Add new columns to job_applications table."""
    print("Starting database migration...")

    # First ensure tables exist
    init_db()

    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'job_applications'
                AND column_name = 'employee_username'
            """))

            if result.fetchone():
                print("✅ Columns already exist, no migration needed")
                return

            # Add new columns
            print("Adding employee_username column...")
            conn.execute(text("""
                ALTER TABLE job_applications
                ADD COLUMN IF NOT EXISTS employee_username VARCHAR(255)
            """))

            print("Adding employee_email column...")
            conn.execute(text("""
                ALTER TABLE job_applications
                ADD COLUMN IF NOT EXISTS employee_email VARCHAR(255)
            """))

            print("Adding employee_phone column...")
            conn.execute(text("""
                ALTER TABLE job_applications
                ADD COLUMN IF NOT EXISTS employee_phone VARCHAR(50)
            """))

            print("Adding employee_description column...")
            conn.execute(text("""
                ALTER TABLE job_applications
                ADD COLUMN IF NOT EXISTS employee_description TEXT
            """))

            conn.commit()
            print("✅ Migration completed successfully!")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    migrate()
