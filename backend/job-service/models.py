"""
Database models for jobs and applications.
Single Responsibility: Defines only database schema/models.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, Integer, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base
import enum
import json


class ApplicationStatus(enum.Enum):
    """Application status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Job(Base):
    """
    Job posting model.
    """
    __tablename__ = "jobs"

    # Primary key
    job_id = Column(Integer, primary_key=True, autoincrement=True)

    # Employer who posted the job
    employer_id = Column(String(255), nullable=False, index=True)

    # Job details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    salary = Column(Float, nullable=True)
    skills = Column(Text, nullable=True)  # Stored as comma-separated values

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "job_id": self.job_id,
            "employer_id": self.employer_id,
            "title": self.title,
            "description": self.description,
            "salary": self.salary,
            "skills": self.skills.split(',') if self.skills else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class JobApplication(Base):
    """
    Job application model.
    """
    __tablename__ = "job_applications"

    # Primary key
    application_id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    job_id = Column(Integer, ForeignKey('jobs.job_id'), nullable=False, index=True)
    employee_id = Column(String(255), nullable=False, index=True)

    # Application details
    cv_url = Column(String(500), nullable=False)
    portfolio_url = Column(String(500), nullable=True)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.PENDING)

    # Employee profile information (cached from user-service)
    employee_username = Column(String(255), nullable=True)
    employee_email = Column(String(255), nullable=True)
    employee_phone = Column(String(50), nullable=True)
    employee_description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "application_id": self.application_id,
            "job_id": self.job_id,
            "employee_id": self.employee_id,
            "cv_url": self.cv_url,
            "portfolio_url": self.portfolio_url,
            "status": self.status.value if self.status else None,
            "employee_profile": {
                "username": self.employee_username,
                "email": self.employee_email,
                "phone": self.employee_phone,
                "description": self.employee_description,
            } if self.employee_username else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Event(Base):
    """
    Event sourcing model - stores domain events.
    This table acts as an event store for audit trail and event replay.
    """
    __tablename__ = "events"

    # Primary key
    event_id = Column(Integer, primary_key=True, autoincrement=True)

    # Event metadata
    event_type = Column(String(100), nullable=False, index=True)  # e.g., "ApplicationAccepted"
    aggregate_id = Column(String(255), nullable=False, index=True)  # e.g., application_id
    aggregate_type = Column(String(100), nullable=False)  # e.g., "JobApplication"

    # Event payload (stored as JSON)
    event_data = Column(JSON, nullable=False)

    # Metadata
    user_id = Column(String(255), nullable=True)  # Who triggered the event
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Event versioning (for schema evolution)
    version = Column(Integer, nullable=False, default=1)

    def to_dict(self):
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "event_data": self.event_data,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "version": self.version,
        }
