"""
User-related query definitions.
Queries represent read operations that don't modify state.
"""
from dataclasses import dataclass


@dataclass
class GetUserProfileByIdQuery:
    """Query to get a user profile by user ID."""
    user_id: str


@dataclass
class GetUserProfileByUsernameQuery:
    """Query to get a user profile by username."""
    username: str


@dataclass
class GetAllUserProfilesQuery:
    """Query to get all user profiles."""
    pass
