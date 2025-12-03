"""
API routes for user profile management.
Single Responsibility: Handles only HTTP request/response logic.
"""
from flask import Blueprint, jsonify, request, send_from_directory
from database import get_db
from repositories import UserProfileRepository
from services import UserProfileService
import os

# Create blueprint
user_bp = Blueprint('users', __name__, url_prefix='/api/users')


def get_service():
    """
    Dependency injection helper.
    Creates service with repository dependency.
    """
    db = next(get_db())
    repository = UserProfileRepository(db)
    service = UserProfileService(repository)
    return service


@user_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "user-service ok"}), 200


@user_bp.route("/profile", methods=["POST"])
def create_profile():
    """
    Create a new user profile.
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

        service = get_service()
        profile = service.create_profile(
            user_id=data["user_id"],
            username=data["username"],
            email=data["email"],
            role=data["role"]
        )

        return jsonify({"message": "Profile created", "profile": profile}), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"❌ Error creating profile: {e}")
        return jsonify({"error": "Internal server error"}), 500


@user_bp.route("/profile/<user_id>", methods=["GET"])
def get_profile(user_id):
    """Get user profile by ID."""
    try:
        service = get_service()
        profile = service.get_profile(user_id)

        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify({"profile": profile}), 200

    except Exception as e:
        print(f"❌ Error getting profile: {e}")
        return jsonify({"error": "Internal server error"}), 500


@user_bp.route("/profile/<user_id>", methods=["PUT", "PATCH"])
def update_profile(user_id):
    """
    Update user profile.
    Expected JSON body (all fields optional):
    {
        "description": "About me...",
        "phone_number": "+1234567890",
        "secondary_email": "second@example.com",
        "address": "123 Main St, City, Country"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        service = get_service()
        profile = service.update_profile(user_id, data)

        if not profile:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify({"message": "Profile updated", "profile": profile}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        return jsonify({"error": "Internal server error"}), 500


@user_bp.route("/profile/<user_id>/picture", methods=["POST"])
def upload_profile_picture(user_id):
    """
    Upload profile picture.
    Expected JSON body:
    {
        "image": "base64-encoded-image-data"
    }
    """
    try:
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400

        service = get_service()
        url = service.upload_profile_picture(user_id, data["image"])

        return jsonify({"message": "Picture uploaded", "url": url}), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"❌ Error uploading picture: {e}")
        return jsonify({"error": "Internal server error"}), 500


@user_bp.route("/uploads/<filename>", methods=["GET"])
def serve_upload(filename):
    """Serve uploaded files."""
    upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
    return send_from_directory(upload_dir, filename)


@user_bp.route("/profile/<user_id>", methods=["DELETE"])
def delete_profile(user_id):
    """Delete user profile."""
    try:
        service = get_service()
        success = service.delete_profile(user_id)

        if not success:
            return jsonify({"error": "Profile not found"}), 404

        return jsonify({"message": "Profile deleted"}), 200

    except Exception as e:
        print(f"❌ Error deleting profile: {e}")
        return jsonify({"error": "Internal server error"}), 500
