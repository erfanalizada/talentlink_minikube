"""
Query handlers for read operations.
Handlers execute queries using the existing service layer.
"""
from typing import List, Optional
from services import UserProfileService
from models import UserProfile
from cqrs.queries import (
    GetUserProfileByIdQuery,
    GetUserProfileByUsernameQuery,
    GetAllUserProfilesQuery
)


class UserQueryHandler:
    """Handler for user-related queries."""

    def __init__(self, service: UserProfileService):
        self.service = service

    def handle_get_profile_by_id(self, query: GetUserProfileByIdQuery) -> Optional[UserProfile]:
        """
        Handle GetUserProfileByIdQuery.
        Returns a user profile by user ID.
        """
        return self.service.get_profile(query.user_id)

    def handle_get_profile_by_username(self, query: GetUserProfileByUsernameQuery) -> Optional[UserProfile]:
        """
        Handle GetUserProfileByUsernameQuery.
        Returns a user profile by username.
        """
        # Access repository directly for this query since service doesn't have a get_by_username method
        return self.service.repository.get_by_username(query.username)

    def handle_get_all_profiles(self, query: GetAllUserProfilesQuery) -> List[UserProfile]:
        """
        Handle GetAllUserProfilesQuery.
        Returns all user profiles.
        """
        # Access repository directly for this query since service doesn't have a get_all method
        return self.service.repository.get_all()
