"""
Test script to verify database connectivity and data persistence.
Run this to check if the database is working correctly.
"""
from database import create_db_session, init_db
from models import UserProfile, UserRole
from repositories import UserProfileRepository

def test_database():
    """Test database operations."""
    print("=" * 50)
    print("Testing Database Connection and Operations")
    print("=" * 50)

    # Initialize database
    init_db()

    # Create a session
    db = create_db_session()
    repo = UserProfileRepository(db)

    try:
        # Test 1: Create a test profile
        print("\n1. Creating test profile...")
        test_user_id = "test-user-123"

        # Check if profile exists
        existing = repo.get_by_id(test_user_id)
        if existing:
            print(f"  ⚠️ Test profile already exists, deleting it first...")
            repo.delete(test_user_id)

        # Create new profile
        profile = repo.create(
            user_id=test_user_id,
            username="testuser",
            email="test@example.com",
            role=UserRole.EMPLOYEE
        )
        print(f"  ✅ Profile created: {profile.user_id}")

        # Test 2: Read the profile
        print("\n2. Reading profile from database...")
        retrieved = repo.get_by_id(test_user_id)
        if retrieved:
            print(f"  ✅ Profile found: {retrieved.username}")
        else:
            print(f"  ❌ Profile not found!")
            return

        # Test 3: Update the profile
        print("\n3. Updating profile...")
        update_data = {
            "description": "This is a test description",
            "phone_number": "+1234567890",
            "address": "123 Test Street"
        }
        updated = repo.update(test_user_id, **update_data)
        if updated:
            print(f"  ✅ Profile updated")
        else:
            print(f"  ❌ Update failed!")
            return

        # Test 4: Verify the update persisted
        print("\n4. Verifying update persisted...")
        db.close()  # Close and reopen session to ensure fresh read
        db = create_db_session()
        repo = UserProfileRepository(db)

        verified = repo.get_by_id(test_user_id)
        if verified:
            print(f"  Description: {verified.description}")
            print(f"  Phone: {verified.phone_number}")
            print(f"  Address: {verified.address}")

            if verified.description == update_data["description"]:
                print(f"  ✅ Description persisted correctly")
            else:
                print(f"  ❌ Description mismatch!")

            if verified.phone_number == update_data["phone_number"]:
                print(f"  ✅ Phone persisted correctly")
            else:
                print(f"  ❌ Phone mismatch!")

            if verified.address == update_data["address"]:
                print(f"  ✅ Address persisted correctly")
            else:
                print(f"  ❌ Address mismatch!")
        else:
            print(f"  ❌ Could not retrieve profile after update!")

        # Test 5: Clean up
        print("\n5. Cleaning up test data...")
        repo.delete(test_user_id)
        print(f"  ✅ Test profile deleted")

        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_database()
