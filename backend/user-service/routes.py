"""
API routes for user profile management.
Single Responsibility: Handles only HTTP request/response logic.
"""
from flask import Blueprint, jsonify, request, send_from_directory
from database import create_db_session
from repositories import UserProfileRepository
from services import UserProfileService
from cqrs.handlers import UserCommandHandler, UserQueryHandler
from cqrs.commands import (
    CreateUserProfileCommand,
    UpdateUserProfileCommand,
    DeleteUserProfileCommand,
    UploadProfilePictureCommand
)
from cqrs.queries import (
    GetUserProfileByIdQuery,
    GetUserProfileByUsernameQuery,
    GetAllUserProfilesQuery
)
import os

# Create blueprint
user_bp = Blueprint('users', __name__, url_prefix='/api/users')


def get_service():
    """
    Dependency injection helper (legacy - for debug endpoints).
    Creates service with repository dependency.
    Returns both service and db session for proper cleanup.
    """
    db = create_db_session()
    repository = UserProfileRepository(db)
    service = UserProfileService(repository)
    return service, db


def get_handlers():
    """
    Factory function for user CQRS handlers.
    Returns command handler, query handler, and db session for proper cleanup.
    """
    db = create_db_session()
    repository = UserProfileRepository(db)
    service = UserProfileService(repository)
    command_handler = UserCommandHandler(service, db_session=db)
    query_handler = UserQueryHandler(service)
    return command_handler, query_handler, db


@user_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "user-service ok"}), 200


@user_bp.route("/debug/test-write-read", methods=["POST"])
def test_write_read():
    """Test endpoint to verify write and read use the same database."""
    try:
        from database import create_db_session, DATABASE_URL, engine
        from models import UserProfile, UserRole
        from repositories import UserProfileRepository
        import uuid
        from sqlalchemy import text

        print("\n" + "=" * 60)
        print("🧪 TESTING WRITE AND READ OPERATIONS")
        print("=" * 60)

        # Create unique test user
        test_user_id = f"test-{uuid.uuid4()}"
        test_description = f"Test description {uuid.uuid4()}"

        print(f"🔍 Using DATABASE_URL: {DATABASE_URL}")

        # STEP 1: Write to database
        print(f"\n📝 STEP 1: Writing test profile...")
        db1 = create_db_session()
        repo1 = UserProfileRepository(db1)

        try:
            # Check which database we're connected to
            result = db1.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"   Connected to: {db_info[0]} as {db_info[1]}")

            profile = repo1.create(
                user_id=test_user_id,
                username=f"testuser-{uuid.uuid4()}",
                email=f"test-{uuid.uuid4()}@example.com",
                role=UserRole.EMPLOYEE
            )
            print(f"   ✅ Profile created with user_id: {test_user_id}")

            # Update it
            updated = repo1.update(test_user_id, description=test_description)
            print(f"   ✅ Profile updated with description: {test_description}")
        finally:
            db1.close()

        # STEP 2: Read from database in NEW session
        print(f"\n📖 STEP 2: Reading back in new session...")
        db2 = create_db_session()
        repo2 = UserProfileRepository(db2)

        try:
            # Check which database we're connected to
            result = db2.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"   Connected to: {db_info[0]} as {db_info[1]}")

            retrieved = repo2.get_by_id(test_user_id)

            if not retrieved:
                print(f"   ❌ FAILED: Profile not found!")
                return jsonify({
                    "status": "FAILED",
                    "error": "Profile not found after creation",
                    "test_user_id": test_user_id,
                    "database_url": str(engine.url)
                }), 500

            print(f"   ✅ Profile found!")
            print(f"   Description in DB: {retrieved.description}")

            # STEP 3: Verify description matches
            print(f"\n✅ STEP 3: Verifying data integrity...")
            if retrieved.description == test_description:
                print(f"   ✅ SUCCESS: Description matches!")
            else:
                print(f"   ❌ FAILED: Description mismatch!")
                print(f"      Expected: {test_description}")
                print(f"      Got: {retrieved.description}")
                return jsonify({
                    "status": "FAILED",
                    "error": "Description mismatch",
                    "expected": test_description,
                    "got": retrieved.description
                }), 500

            # STEP 4: Cleanup
            print(f"\n🧹 STEP 4: Cleaning up...")
            repo2.delete(test_user_id)
            print(f"   ✅ Test profile deleted")

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED - DATABASE IS WORKING CORRECTLY")
            print("=" * 60 + "\n")

            return jsonify({
                "status": "SUCCESS",
                "message": "Write and read are using the same database",
                "test_user_id": test_user_id,
                "test_description": test_description,
                "retrieved_description": retrieved.description,
                "database_url": str(engine.url),
                "database_name": db_info[0],
                "database_user": db_info[1]
            }), 200

        finally:
            db2.close()

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "FAILED",
            "error": str(e)
        }), 500


@user_bp.route("/debug/profile/<user_id>", methods=["GET"])
def debug_profile(user_id):
    """Debug endpoint to check raw database state."""
    try:
        from database import create_db_session, DATABASE_URL, engine
        from models import UserProfile
        from sqlalchemy import text

        # Show connection info
        print(f"🔍 DATABASE_URL: {DATABASE_URL}")
        print(f"🔍 Engine URL: {engine.url}")

        db = create_db_session()
        try:
            # Test connection
            result = db.execute(text("SELECT current_database(), current_user;"))
            db_info = result.fetchone()
            print(f"🔍 Connected to database: {db_info[0]}, user: {db_info[1]}")

            # Query directly from database
            profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

            if not profile:
                # List all profiles in database
                all_profiles = db.query(UserProfile).all()
                return jsonify({
                    "error": "Profile not found in database",
                    "user_id": user_id,
                    "database_url": str(engine.url),
                    "database_name": db_info[0],
                    "database_user": db_info[1],
                    "total_profiles_in_db": len(all_profiles),
                    "existing_user_ids": [p.user_id for p in all_profiles[:10]]
                }), 404

            # Return raw database values
            return jsonify({
                "message": "Raw database state",
                "database_url": str(engine.url),
                "database_name": db_info[0],
                "database_user": db_info[1],
                "database_values": {
                    "user_id": profile.user_id,
                    "username": profile.username,
                    "email": profile.email,
                    "role": profile.role.value if profile.role else None,
                    "description": profile.description,
                    "phone_number": profile.phone_number,
                    "secondary_email": profile.secondary_email,
                    "address": profile.address,
                    "profile_picture_url": profile.profile_picture_url,
                    "created_at": str(profile.created_at),
                    "updated_at": str(profile.updated_at),
                }
            }), 200
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@user_bp.route("/profile", methods=["POST"])
def create_profile():
    """
    Create a new user profile - COMMAND.
    Expected JSON body:
    {
        "user_id": "keycloak-user-id",
        "username": "username",
        "email": "email@example.com",
        "role": "employee" | "employer"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["user_id", "username", "email", "role"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        # Create command
        command = CreateUserProfileCommand(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            role=data["role"],
            description=data.get("description"),
            phone_number=data.get("phone_number"),
            secondary_email=data.get("secondary_email"),
            address=data.get("address")
        )

        # Execute command
        command_handler, _, db = get_handlers()
        try:
            profile = command_handler.handle_create_profile(command)
            return jsonify(profile), 201
        finally:
            db.close()

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        return jsonify({"error": "Internal server error"}), 500


@user_bp.route("/profile/<user_id>", methods=["GET"])
def get_profile(user_id):
    """Get user profile by ID - QUERY."""
    try:
        # Create query
        query = GetUserProfileByIdQuery(user_id=user_id)

        # Execute query
        _, query_handler, db = get_handlers()
        try:
            profile = query_handler.handle_get_profile_by_id(query)

            if not profile:
                return jsonify({"error": "Profile not found"}), 404

            return jsonify(profile), 200
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return jsonify({"error": "Internal server error"}), 500


@user_bp.route("/profile/<user_id>", methods=["PUT", "PATCH"])
def update_profile(user_id):
    """
    Update user profile - COMMAND.
    Expected JSON body (all fields optional):
    {
        "description": "About me...",
        "phone_number": "+1234567890",
        "secondary_email": "second@example.com",
        "address": "123 Main St, City, Country"
    }
    """
    try:
        print(f"\n{'='*60}")
        print(f"📝 UPDATE PROFILE REQUEST for user_id: {user_id}")
        print(f"{'='*60}")
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request data length: {len(request.data) if request.data else 0}")

        # Try to get JSON data
        try:
            data = request.get_json()
            if data is None:
                print(f"⚠️ request.get_json() returned None")
                print(f"Raw data: {request.data}")
                return jsonify({"error": "Invalid JSON or empty request body"}), 400

            print(f"📦 Received data keys: {list(data.keys())}")
            print(f"📦 Received data: {data}")

        except Exception as json_error:
            print(f"❌ JSON parsing error: {json_error}")
            print(f"Raw request data: {request.data}")
            return jsonify({"error": f"Invalid JSON: {str(json_error)}"}), 400

        if not data:
            print(f"⚠️ Data dictionary is empty")
            return jsonify({"error": "No data provided"}), 400

        # Create command
        command = UpdateUserProfileCommand(
            user_id=user_id,
            username=data.get("username"),
            email=data.get("email"),
            description=data.get("description"),
            phone_number=data.get("phone_number"),
            secondary_email=data.get("secondary_email"),
            address=data.get("address")
        )

        # Execute command
        command_handler, _, db = get_handlers()
        try:
            print(f"🔄 Calling command_handler.handle_update_profile...")
            profile = command_handler.handle_update_profile(command)

            if not profile:
                print(f"⚠️ Profile not found for user_id: {user_id}")
                return jsonify({"error": "Profile not found"}), 404

            print(f"✅ Profile updated successfully for user {user_id}")
            print(f"{'='*60}\n")
            return jsonify(profile), 200
        finally:
            db.close()

    except ValueError as e:
        print(f"⚠️ Validation error updating profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@user_bp.route("/profile/<user_id>/picture", methods=["POST"])
def upload_profile_picture(user_id):
    """
    Upload profile picture - COMMAND.
    Expected JSON body:
    {
        "image": "base64-encoded-image-data"
    }
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400

        print(f"📷 Uploading profile picture for user {user_id}")

        # Create command
        command = UploadProfilePictureCommand(
            user_id=user_id,
            image_base64=data["image"]
        )

        # Execute command
        command_handler, _, db = get_handlers()
        try:
            url = command_handler.handle_upload_profile_picture(command)

            if not url:
                return jsonify({"error": "Failed to upload picture"}), 500

            print(f"✅ Picture uploaded successfully for user {user_id}: {url}")
            return jsonify({"profile_picture_url": url}), 200
        finally:
            db.close()

    except ValueError as e:
        print(f"⚠️ Validation error uploading picture: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"❌ Error uploading picture: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@user_bp.route("/uploads/<filename>", methods=["GET"])
def serve_upload(filename):
    """Serve uploaded files."""
    upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
    return send_from_directory(upload_dir, filename)


@user_bp.route("/profile/<user_id>", methods=["DELETE"])
def delete_profile(user_id):
    """Delete user profile - COMMAND."""
    try:
        # Create command
        command = DeleteUserProfileCommand(user_id=user_id)

        # Execute command
        command_handler, _, db = get_handlers()
        try:
            success = command_handler.handle_delete_profile(command)

            if not success:
                return jsonify({"error": "Profile not found"}), 404

            return jsonify({"message": "Profile deleted"}), 200
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Error deleting profile: {e}")
        return jsonify({"error": "Internal server error"}), 500
