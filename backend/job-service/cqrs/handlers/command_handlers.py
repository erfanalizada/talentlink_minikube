"""
Command handlers for write operations.
Handlers execute commands using the existing service layer.
"""
from typing import Optional
from services import JobService, JobApplicationService
from models import Job, JobApplication
from cqrs.commands import (
    CreateJobCommand,
    UpdateJobCommand,
    DeleteJobCommand,
    ApplyToJobCommand,
    UpdateApplicationStatusCommand
)


class JobCommandHandler:
    """Handler for job-related commands."""

    def __init__(self, service: JobService):
        self.service = service

    def handle_create_job(self, command: CreateJobCommand) -> Job:
        """
        Handle CreateJobCommand.
        Creates a new job posting.
        """
        return self.service.create_job(
            employer_id=command.employer_id,
            title=command.title,
            description=command.description,
            salary=command.salary,
            skills=command.skills
        )

    def handle_update_job(self, command: UpdateJobCommand) -> Optional[Job]:
        """
        Handle UpdateJobCommand.
        Updates an existing job posting.
        """
        return self.service.update_job(
            job_id=command.job_id,
            employer_id=command.employer_id,
            title=command.title,
            description=command.description,
            salary=command.salary,
            skills=command.skills
        )

    def handle_delete_job(self, command: DeleteJobCommand) -> bool:
        """
        Handle DeleteJobCommand.
        Deletes a job posting.
        """
        return self.service.delete_job(
            job_id=command.job_id,
            employer_id=command.employer_id
        )


class ApplicationCommandHandler:
    """Handler for application-related commands."""

    def __init__(self, service: JobApplicationService):
        self.service = service

    def handle_apply_to_job(self, command: ApplyToJobCommand) -> JobApplication:
        """
        Handle ApplyToJobCommand.
        Creates a new job application.
        """
        return self.service.create_application(
            job_id=command.job_id,
            employee_id=command.employee_id,
            cv_base64=command.cv_base64,
            portfolio_url=command.portfolio_url,
            cv_url=command.cv_url
        )

    def handle_update_application_status(self, command: UpdateApplicationStatusCommand) -> Optional[JobApplication]:
        """
        Handle UpdateApplicationStatusCommand.
        Updates the status of an application.
        """
        return self.service.update_application_status(
            application_id=command.application_id,
            employer_id=command.employer_id,
            status=command.status
        )
