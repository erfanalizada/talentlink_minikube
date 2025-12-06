"""
Job-related query definitions.
Queries represent read operations that don't modify state.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class GetAllJobsQuery:
    """Query to get all job postings."""
    pass


@dataclass
class GetJobByIdQuery:
    """Query to get a specific job by ID."""
    job_id: int
    employee_id: Optional[str] = None  # For has_applied flag


@dataclass
class GetJobsByEmployerQuery:
    """Query to get all jobs posted by a specific employer."""
    employer_id: str


@dataclass
class GetAllJobsWithApplicationStatusQuery:
    """Query to get all jobs with application status for an employee."""
    employee_id: str
