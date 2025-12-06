"""
Application-related query definitions.
Queries represent read operations that don't modify state.
"""
from dataclasses import dataclass


@dataclass
class GetApplicationsByJobQuery:
    """Query to get all applications for a specific job."""
    job_id: int
    employer_id: str


@dataclass
class GetApplicationsByEmployeeQuery:
    """Query to get all applications submitted by an employee."""
    employee_id: str
