"""
Service layer for business logic.
Single Responsibility: Handles business logic and validation.
"""
import os
import base64
from typing import List, Optional, Dict
from models import Job, JobApplication, ApplicationStatus
from repositories import IJobRepository, IJobApplicationRepository
from PIL import Image
from io import BytesIO


class JobService:
    """Service for managing jobs."""

    def __init__(self, repository: IJobRepository):
        self.repository = repository

    def create_job(self, employer_id: str, title: str, description: str,
                   salary: Optional[float], skills: Optional[List[str]]) -> Job:
        """Create a new job posting."""
        # Validation
        if not title or len(title.strip()) == 0:
            raise ValueError("Job title is required")
        if not description or len(description.strip()) == 0:
            raise ValueError("Job description is required")

        # Convert skills list to comma-separated string
        skills_str = ','.join(skills) if skills else None

        job = Job(
            employer_id=employer_id,
            title=title.strip(),
            description=description.strip(),
            salary=salary,
            skills=skills_str
        )
        return self.repository.create(job)

    def get_job(self, job_id: int) -> Optional[Job]:
        """Get a job by ID."""
        return self.repository.get_by_id(job_id)

    def get_all_jobs(self) -> List[Job]:
        """Get all jobs."""
        return self.repository.get_all()

    def get_jobs_by_employer(self, employer_id: str) -> List[Job]:
        """Get all jobs posted by a specific employer."""
        return self.repository.get_by_employer(employer_id)

    def update_job(self, job_id: int, employer_id: str, title: Optional[str] = None,
                   description: Optional[str] = None, salary: Optional[float] = None,
                   skills: Optional[List[str]] = None) -> Optional[Job]:
        """Update a job posting."""
        job = self.repository.get_by_id(job_id)
        if not job:
            return None

        # Verify ownership
        if job.employer_id != employer_id:
            raise PermissionError("You can only update your own job postings")

        # Update fields
        if title is not None:
            if len(title.strip()) == 0:
                raise ValueError("Job title cannot be empty")
            job.title = title.strip()
        if description is not None:
            if len(description.strip()) == 0:
                raise ValueError("Job description cannot be empty")
            job.description = description.strip()
        if salary is not None:
            job.salary = salary
        if skills is not None:
            job.skills = ','.join(skills) if skills else None

        return self.repository.update(job)

    def delete_job(self, job_id: int, employer_id: str) -> bool:
        """Delete a job posting."""
        job = self.repository.get_by_id(job_id)
        if not job:
            return False

        # Verify ownership
        if job.employer_id != employer_id:
            raise PermissionError("You can only delete your own job postings")

        return self.repository.delete(job_id)


class JobApplicationService:
    """Service for managing job applications."""

    def __init__(self, repository: IJobApplicationRepository, job_repository: IJobRepository):
        self.repository = repository
        self.job_repository = job_repository

    def create_application(self, job_id: int, employee_id: str,
                          cv_base64: Optional[str] = None, portfolio_url: Optional[str] = None,
                          cv_url: Optional[str] = None) -> JobApplication:
        """Create a new job application."""
        # Verify job exists
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")

        # Check if employee already applied
        existing_apps = self.repository.get_by_employee(employee_id)
        for app in existing_apps:
            if app.job_id == job_id:
                raise ValueError("You have already applied to this job")

        # Determine CV URL: either an already-saved file (cv_url provided)
        # or save from base64 payload
        if cv_url is None:
            if not cv_base64:
                raise ValueError("cv is required")
            cv_url = self._save_cv(employee_id, job_id, cv_base64)

        application = JobApplication(
            job_id=job_id,
            employee_id=employee_id,
            cv_url=cv_url,
            portfolio_url=portfolio_url if portfolio_url else None,
            status=ApplicationStatus.PENDING
        )
        return self.repository.create(application)

    def get_application(self, application_id: int) -> Optional[JobApplication]:
        """Get an application by ID."""
        return self.repository.get_by_id(application_id)

    def get_applications_by_job(self, job_id: int, employer_id: str) -> List[JobApplication]:
        """Get all applications for a specific job."""
        # Verify job ownership
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        if job.employer_id != employer_id:
            raise PermissionError("You can only view applications for your own jobs")

        return self.repository.get_by_job(job_id)

    def get_applications_by_employee(self, employee_id: str) -> List[JobApplication]:
        """Get all applications submitted by a specific employee."""
        return self.repository.get_by_employee(employee_id)

    def update_application_status(self, application_id: int, employer_id: str,
                                  status: str) -> Optional[JobApplication]:
        """Update the status of an application."""
        application = self.repository.get_by_id(application_id)
        if not application:
            return None

        # Verify job ownership
        job = self.job_repository.get_by_id(application.job_id)
        if not job or job.employer_id != employer_id:
            raise PermissionError("You can only update applications for your own jobs")

        # Validate status
        try:
            application.status = ApplicationStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}")

        return self.repository.update(application)

    def _save_cv(self, employee_id: str, job_id: int, cv_base64: str) -> str:
        """Save CV file from base64 data."""
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = "/app/uploads/cvs"
            os.makedirs(upload_dir, exist_ok=True)

            # Decode base64
            cv_data = base64.b64decode(cv_base64)

            # Save file
            filename = f"{employee_id}_{job_id}.pdf"
            filepath = os.path.join(upload_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(cv_data)

            # Return URL path
            return f"/api/jobs/uploads/cvs/{filename}"
        except Exception as e:
            raise ValueError(f"Failed to save CV: {str(e)}")
