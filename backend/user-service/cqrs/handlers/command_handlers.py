"""
Command handlers for write operations.
Handlers execute commands using the existing service layer.
"""
from typing import Optional
from services import UserProfileService
from models import UserProfile
from cqrs.commands import (
    CreateUserProfileCommand,
    UpdateUserProfileCommand,
    DeleteUserProfileCommand,
    UploadProfilePictureCommand
)


class UserCommandHandler:
    """Handler for user-related commands."""

    def __init__(self, service: UserProfileService):
        self.service = service

    def handle_create_profile(self, command: CreateUserProfileCommand) -> UserProfile:
        """
        Handle CreateUserProfileCommand.
        Creates a new user profile.
        """
        return self.service.create_profile(
            user_id=command.user_id,
            username=command.username,
            email=command.email,
            role=command.role,
            description=command.description,
            phone_number=command.phone_number,
            secondary_email=command.secondary_email,
            address=command.address
        )

    def handle_update_profile(self, command: UpdateUserProfileCommand) -> Optional[UserProfile]:
        """
        Handle UpdateUserProfileCommand.
        Updates an existing user profile.
        """
        # Build update dictionary from non-None values
        updates = {}
        if command.username is not None:
            updates['username'] = command.username
        if command.email is not None:
            updates['email'] = command.email
        if command.description is not None:
            updates['description'] = command.description
        if command.phone_number is not None:
            updates['phone_number'] = command.phone_number
        if command.secondary_email is not None:
            updates['secondary_email'] = command.secondary_email
        if command.address is not None:
            updates['address'] = command.address

        return self.service.update_profile(command.user_id, updates)

    def handle_delete_profile(self, command: DeleteUserProfileCommand) -> bool:
        """
        Handle DeleteUserProfileCommand.
        Deletes a user profile.
        """
        return self.service.delete_profile(command.user_id)

    def handle_upload_profile_picture(self, command: UploadProfilePictureCommand) -> str:
        """
        Handle UploadProfilePictureCommand.
        Uploads and sets a profile picture.
        Returns the URL of the uploaded picture.
        """
        return self.service.upload_profile_picture(command.user_id, command.image_base64)
