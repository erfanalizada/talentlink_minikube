"""
CQRS (Command Query Responsibility Segregation) implementation for User service.
"""
from .commands import (
    CreateUserProfileCommand,
    UpdateUserProfileCommand,
    DeleteUserProfileCommand,
    UploadProfilePictureCommand
)
from .queries import (
    GetUserProfileByIdQuery,
    GetUserProfileByUsernameQuery,
    GetAllUserProfilesQuery
)
from .handlers import UserCommandHandler, UserQueryHandler

__all__ = [
    # Commands
    'CreateUserProfileCommand',
    'UpdateUserProfileCommand',
    'DeleteUserProfileCommand',
    'UploadProfilePictureCommand',
    # Queries
    'GetUserProfileByIdQuery',
    'GetUserProfileByUsernameQuery',
    'GetAllUserProfilesQuery',
    # Handlers
    'UserCommandHandler',
    'UserQueryHandler',
]
