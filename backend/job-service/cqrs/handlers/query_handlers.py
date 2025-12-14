"""
Query handlers for read operations.
Handlers execute queries using the existing service layer.
Implements Redis caching for performance optimization.
"""
from typing import List, Optional, Dict
from services import JobService, JobApplicationService
from models import Job, JobApplication
from repositories import JobApplicationRepository
from cache import cache_query
from cqrs.queries import (
    GetAllJobsQuery,
    GetJobByIdQuery,
    GetJobsByEmployerQuery,
    GetAllJobsWithApplicationStatusQuery,
    GetApplicationsByJobQuery,
    GetApplicationsByEmployeeQuery
)


class JobQueryHandler:
    """Handler for job-related queries."""

    def __init__(self, service: JobService):
        self.service = service

    @cache_query("jobs:all", ttl=300)
    def handle_get_all_jobs(self, query: GetAllJobsQuery) -> List[Job]:
        """
        Handle GetAllJobsQuery.
        Returns all job postings.
        Cached for 5 minutes.
        """
        return self.service.get_all_jobs()

    @cache_query("jobs:by_id", ttl=600)
    def handle_get_job_by_id(self, query: GetJobByIdQuery) -> Optional[Job]:
        """
        Handle GetJobByIdQuery.
        Returns a specific job by ID.
        Cached for 10 minutes.
        """
        return self.service.get_job(query.job_id)

    @cache_query("jobs:by_employer", ttl=300)
    def handle_get_jobs_by_employer(self, query: GetJobsByEmployerQuery) -> List[Job]:
        """
        Handle GetJobsByEmployerQuery.
        Returns all jobs posted by a specific employer.
        Cached for 5 minutes.
        """
        return self.service.get_jobs_by_employer(query.employer_id)

    @cache_query("jobs:with_status", ttl=180)
    def handle_get_all_jobs_with_application_status(self, query: GetAllJobsWithApplicationStatusQuery) -> List[Dict]:
        """
        Handle GetAllJobsWithApplicationStatusQuery.
        Returns all jobs with application status for an employee.
        Optimized for employee job browsing.
        Cached for 3 minutes (shorter TTL for personalized data).
        """
        return self.service.get_all_jobs_with_application_status(query.employee_id)


class ApplicationQueryHandler:
    """Handler for application-related queries."""

    def __init__(self, service: JobApplicationService):
        self.service = service

    def handle_get_applications_by_job(self, query: GetApplicationsByJobQuery) -> List[JobApplication]:
        """
        Handle GetApplicationsByJobQuery.
        Returns all applications for a specific job.
        Optimized for employer viewing applicants.
        """
        return self.service.get_applications_by_job(
            job_id=query.job_id,
            employer_id=query.employer_id
        )

    def handle_get_applications_by_employee(self, query: GetApplicationsByEmployeeQuery) -> List[JobApplication]:
        """
        Handle GetApplicationsByEmployeeQuery.
        Returns all applications submitted by an employee.
        Optimized for employee viewing their applications.
        """
        return self.service.get_applications_by_employee(query.employee_id)
