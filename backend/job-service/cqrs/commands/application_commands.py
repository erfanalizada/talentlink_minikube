"""
Application-related command definitions.
Commands represent write operations that modify state.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ApplyToJobCommand:
    """Command to apply to a job posting."""
    job_id: int
    employee_id: str
    cv_base64: Optional[str] = None
    portfolio_url: Optional[str] = None
    cv_url: Optional[str] = None  # For pre-uploaded files


@dataclass
class UpdateApplicationStatusCommand:
    """Command to update an application's status."""
    application_id: int
    employer_id: str
    status: str


@dataclass
class DeleteApplicationCommand:
    """Command to delete an application."""
    application_id: int
    employer_id: str
