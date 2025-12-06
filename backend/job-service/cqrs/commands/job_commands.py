"""
Job-related command definitions.
Commands represent write operations that modify state.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CreateJobCommand:
    """Command to create a new job posting."""
    employer_id: str
    title: str
    description: str
    salary: Optional[float] = None
    skills: Optional[List[str]] = None


@dataclass
class UpdateJobCommand:
    """Command to update an existing job posting."""
    job_id: int
    employer_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[float] = None
    skills: Optional[List[str]] = None


@dataclass
class DeleteJobCommand:
    """Command to delete a job posting."""
    job_id: int
    employer_id: str
