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
from event_publisher import EventPublisher


class UserCommandHandler:
    """Handler for user-related commands with event sourcing."""

    def __init__(self, service: UserProfileService, db_session=None):
        self.service = service
        self.db_session = db_session

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
        Deletes a user profile and publishes UserDeleted event.
        """
        # Get user profile before deletion (need data for event)
        user_profile = self.service.get_profile(command.user_id)

        if not user_profile:
            return False

        # Delete the profile
        success = self.service.delete_profile(command.user_id)

        # If deletion was successful, publish UserDeleted event
        if success:
            self._publish_user_deleted_event(user_profile, command.user_id)

        return success

    def _publish_user_deleted_event(self, user_profile, deleted_by_user_id):
        """
        Publish UserDeleted event to event store and RabbitMQ.

        This event will be consumed by auth-service to delete user from Keycloak.
        """
        if not self.db_session:
            from flask import current_app
            current_app.logger.warning("⚠️ Cannot publish event: no database session provided")
            return

        try:
            # Create event publisher
            publisher = EventPublisher(self.db_session)

            # Prepare event data
            event_data = {
                "user_id": user_profile['user_id'],
                "username": user_profile['username'],
                "email": user_profile['email'],
                "role": user_profile['role'],
                "deleted_at": user_profile.get('updated_at') or user_profile.get('created_at'),
                "deleted_by": deleted_by_user_id
            }

            # Publish event
            publisher.publish_event(
                event_type="UserDeleted",
                aggregate_id=user_profile['user_id'],
                aggregate_type="UserProfile",
                event_data=event_data,
                user_id=deleted_by_user_id
            )

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"❌ Failed to publish UserDeleted event: {e}")
            # Don't raise - deletion already succeeded
            # Event can be retried from event store if needed

    def handle_upload_profile_picture(self, command: UploadProfilePictureCommand) -> str:
        """
        Handle UploadProfilePictureCommand.
        Uploads and sets a profile picture.
        Returns the URL of the uploaded picture.
        """
        return self.service.upload_profile_picture(command.user_id, command.image_base64)
