"""
Query definitions for read operations.
Queries represent requests for data without modifying state.
"""
from .user_queries import (
    GetUserProfileByIdQuery,
    GetUserProfileByUsernameQuery,
    GetAllUserProfilesQuery
)

__all__ = [
    'GetUserProfileByIdQuery',
    'GetUserProfileByUsernameQuery',
    'GetAllUserProfilesQuery',
]
