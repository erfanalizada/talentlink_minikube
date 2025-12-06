"""
User-related command definitions.
Commands represent write operations that modify state.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateUserProfileCommand:
    """Command to create a new user profile."""
    user_id: str
    username: str
    email: str
    role: str
    description: Optional[str] = None
    phone_number: Optional[str] = None
    secondary_email: Optional[str] = None
    address: Optional[str] = None


@dataclass
class UpdateUserProfileCommand:
    """Command to update an existing user profile."""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    secondary_email: Optional[str] = None
    address: Optional[str] = None


@dataclass
class DeleteUserProfileCommand:
    """Command to delete a user profile."""
    user_id: str


@dataclass
class UploadProfilePictureCommand:
    """Command to upload a profile picture."""
    user_id: str
    image_base64: str
