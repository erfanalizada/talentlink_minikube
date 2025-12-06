"""
Query definitions for read operations.
Queries represent requests for data without modifying state.
"""
from .job_queries import (
    GetAllJobsQuery,
    GetJobByIdQuery,
    GetJobsByEmployerQuery,
    GetAllJobsWithApplicationStatusQuery
)
from .application_queries import (
    GetApplicationsByJobQuery,
    GetApplicationsByEmployeeQuery
)

__all__ = [
    'GetAllJobsQuery',
    'GetJobByIdQuery',
    'GetJobsByEmployerQuery',
    'GetAllJobsWithApplicationStatusQuery',
    'GetApplicationsByJobQuery',
    'GetApplicationsByEmployeeQuery',
]
