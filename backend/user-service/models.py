"""
Database models for user profiles.
Single Responsibility: Defines only database schema/models.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(enum.Enum):
    """User role enumeration."""
    EMPLOYEE = "employee"
    EMPLOYER = "employer"


class UserProfile(Base):
    """
    User profile model storing additional user information.
    Keycloak handles authentication, this stores profile data.
    """
    __tablename__ = "user_profiles"

    # Primary key - matches Keycloak user ID
    user_id = Column(String(255), primary_key=True, index=True)

    # Basic info from Keycloak (duplicated for quick access)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    # Extended profile information
    description = Column(Text, nullable=True)
    phone_number = Column(String(50), nullable=True)
    secondary_email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value if self.role else None,
            "description": self.description,
            "phone_number": self.phone_number,
            "secondary_email": self.secondary_email,
            "address": self.address,
            "profile_picture_url": self.profile_picture_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
