"""
Repository layer for data access.
Single Responsibility: Handles only database operations.
Open/Closed: Can extend with new methods without modifying existing ones.
Dependency Inversion: Depends on abstractions (interfaces), not concrete implementations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy.orm import Session
from models import UserProfile, UserRole


class IUserProfileRepository(ABC):
    """
    Interface for UserProfile repository.
    Interface Segregation: Clients depend only on methods they use.
    """

    @abstractmethod
    def create(self, user_id: str, username: str, email: str, role: UserRole) -> UserProfile:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[UserProfile]:
        pass

    @abstractmethod
    def update(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def get_all(self) -> List[UserProfile]:
        pass


class UserProfileRepository(IUserProfileRepository):
    """
    Concrete implementation of UserProfile repository.
    Single Responsibility: Only handles UserProfile data access.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, username: str, email: str, role: UserRole) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            role=role
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_by_id(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile by user ID."""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def get_by_username(self, username: str) -> Optional[UserProfile]:
        """Retrieve user profile by username."""
        return self.db.query(UserProfile).filter(UserProfile.username == username).first()

    def update(self, user_id: str, **kwargs) -> Optional[UserProfile]:
        """Update user profile with provided fields."""
        profile = self.get_by_id(user_id)
        if not profile:
            print(f"⚠️ Profile not found for user_id: {user_id}")
            return None

        print(f"📝 Updating profile {user_id} with: {kwargs}")

        # Update only provided fields (allow empty strings and None)
        updated_fields = []
        for key, value in kwargs.items():
            if hasattr(profile, key):
                old_value = getattr(profile, key)
                setattr(profile, key, value)
                updated_fields.append(f"{key}: {old_value} -> {value}")
                print(f"  ✓ Set {key} = {value}")

        try:
            self.db.commit()
            print(f"✅ Committed changes to database")
            self.db.refresh(profile)
            print(f"✅ Refreshed profile from database")

            # Verify the changes were saved
            verification = self.get_by_id(user_id)
            if verification:
                for key in kwargs.keys():
                    if hasattr(verification, key):
                        saved_value = getattr(verification, key)
                        expected_value = kwargs[key]
                        if saved_value == expected_value:
                            print(f"  ✓ Verified {key} = {saved_value}")
                        else:
                            print(f"  ⚠️ Mismatch {key}: expected {expected_value}, got {saved_value}")

            return profile
        except Exception as e:
            print(f"❌ Error during commit: {e}")
            self.db.rollback()
            raise

    def delete(self, user_id: str) -> bool:
        """Delete user profile."""
        profile = self.get_by_id(user_id)
        if not profile:
            return False

        self.db.delete(profile)
        self.db.commit()
        return True

    def get_all(self) -> List[UserProfile]:
        """Retrieve all user profiles."""
        return self.db.query(UserProfile).all()
