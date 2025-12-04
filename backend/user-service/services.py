"""
Service layer for business logic.
Single Responsibility: Handles only business logic, not data access or HTTP concerns.
Dependency Inversion: Depends on repository abstractions, not concrete implementations.
"""
import os
import base64
from typing import Optional, Dict, Any
from PIL import Image
from io import BytesIO
from repositories import IUserProfileRepository
from models import UserProfile, UserRole


class UserProfileService:
    """
    Service for user profile business logic.
    Single Responsibility: Manages profile operations and business rules.
    """

    def __init__(self, repository: IUserProfileRepository):
        """
        Dependency Injection: Inject repository through constructor.
        Allows easy testing with mock repositories.
        """
        self.repository = repository
        self.upload_dir = os.getenv("UPLOAD_DIR", "/app/uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

    def create_profile(self, user_id: str, username: str, email: str, role: str) -> Dict[str, Any]:
        """
        Create a new user profile.
        Business rule: Validate role before creation.
        """
        try:
            user_role = UserRole(role)
        except ValueError:
            raise ValueError(f"Invalid role: {role}. Must be 'employee' or 'employer'")

        # Check if profile already exists
        existing = self.repository.get_by_id(user_id)
        if existing:
            raise ValueError(f"Profile already exists for user_id: {user_id}")

        profile = self.repository.create(user_id, username, email, user_role)
        return profile.to_dict()

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile by ID."""
        profile = self.repository.get_by_id(user_id)
        return profile.to_dict() if profile else None

    def update_profile(self, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user profile.
        Business rule: Validate and sanitize input data.
        """
        print(f"🔧 Service update_profile called for user_id: {user_id}")
        print(f"🔧 Received data: {data}")

        # Filter allowed fields for update
        allowed_fields = [
            "description", "phone_number", "secondary_email",
            "address", "profile_picture_url"
        ]

        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        print(f"🔧 Filtered update_data: {update_data}")

        # Validate phone number format if provided
        if "phone_number" in update_data:
            phone = update_data["phone_number"]
            print(f"🔧 Validating phone number: {phone}")
            if phone and not self._validate_phone(phone):
                print(f"❌ Phone validation failed: {phone}")
                raise ValueError(f"Invalid phone number format: {phone}")
            print(f"✅ Phone validation passed")

        # Validate email format if provided
        if "secondary_email" in update_data:
            email = update_data["secondary_email"]
            print(f"🔧 Validating secondary email: {email}")
            if email and not self._validate_email(email):
                print(f"❌ Email validation failed: {email}")
                raise ValueError(f"Invalid email format: {email}")
            print(f"✅ Email validation passed")

        print(f"🔧 Calling repository.update with: {update_data}")
        profile = self.repository.update(user_id, **update_data)

        if profile:
            print(f"✅ Service update successful")
            return profile.to_dict()
        else:
            print(f"⚠️ Repository returned None")
            return None

    def upload_profile_picture(self, user_id: str, image_data: str) -> Optional[str]:
        """
        Upload and process profile picture.
        Business rules:
        - Validate image format
        - Resize image to standard size
        - Save with unique filename
        """
        try:
            print(f"📷 Processing profile picture for user {user_id}")

            # Decode base64 image
            if "," in image_data:
                image_data = image_data.split(",")[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))

            print(f"📷 Image format: {image.format}, size: {image.size}")

            # Validate image format
            if image.format not in ["JPEG", "PNG", "JPG"]:
                raise ValueError("Image must be JPEG or PNG")

            # Resize to standard size (keeping aspect ratio)
            max_size = (400, 400)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save with user_id as filename
            format_ext = "jpg" if image.format == "JPEG" else image.format.lower()
            filename = f"{user_id}_profile.{format_ext}"
            filepath = os.path.join(self.upload_dir, filename)

            print(f"📷 Saving to: {filepath}")
            image.save(filepath)

            # Return URL path (will be served by Flask)
            url = f"/api/users/uploads/{filename}"

            # Update profile with new picture URL
            print(f"📷 Updating profile with picture URL: {url}")
            self.repository.update(user_id, profile_picture_url=url)

            print(f"✅ Profile picture uploaded successfully: {url}")
            return url

        except Exception as e:
            print(f"❌ Error in upload_profile_picture: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Failed to upload profile picture: {str(e)}")

    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile."""
        return self.repository.delete(user_id)

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        if not phone or len(phone.strip()) == 0:
            return True  # Empty is valid (will be stored as NULL)

        # Simple validation: remove spaces and check length
        # Allow + for international format
        cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")

        # Must have at least some digits and reasonable length
        if not cleaned.isdigit():
            print(f"⚠️ Phone contains non-digit characters after cleaning: {cleaned}")
            return False

        if not (7 <= len(cleaned) <= 15):
            print(f"⚠️ Phone length invalid: {len(cleaned)} (need 7-15 digits)")
            return False

        return True

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        if not email or len(email.strip()) == 0:
            return True  # Empty is valid (will be stored as NULL)

        # Basic email validation
        if "@" not in email:
            print(f"⚠️ Email missing @ symbol")
            return False

        parts = email.split("@")
        if len(parts) != 2:
            print(f"⚠️ Email has multiple @ symbols")
            return False

        if "." not in parts[1]:
            print(f"⚠️ Email domain missing dot")
            return False

        return True
