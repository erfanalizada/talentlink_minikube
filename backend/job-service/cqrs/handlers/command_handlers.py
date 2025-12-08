"""
Command handlers for write operations.
Handlers execute commands using the existing service layer.
"""
from typing import Optional
from services import JobService, JobApplicationService
from models import Job, JobApplication, ApplicationStatus
from cqrs.commands import (
    CreateJobCommand,
    UpdateJobCommand,
    DeleteJobCommand,
    ApplyToJobCommand,
    UpdateApplicationStatusCommand,
    DeleteApplicationCommand
)
from event_publisher import EventPublisher


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
    """Handler for application-related commands with event sourcing."""

    def __init__(self, service: JobApplicationService, db_session=None):
        self.service = service
        self.db_session = db_session

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
        Updates the status of an application and publishes event if ACCEPTED.
        """
        # Update application status
        application = self.service.update_application_status(
            application_id=command.application_id,
            employer_id=command.employer_id,
            status=command.status
        )

        # If application was accepted, publish ApplicationAccepted event
        if application and application.status == ApplicationStatus.ACCEPTED:
            self._publish_application_accepted_event(application, command.employer_id)

        return application

    def _publish_application_accepted_event(self, application: JobApplication, employer_id: str):
        """
        Publish ApplicationAccepted event to event store and RabbitMQ.

        This event will be consumed by notification-service to send email to employee.
        """
        if not self.db_session:
            from flask import current_app
            current_app.logger.warning("⚠️ Cannot publish event: no database session provided")
            return

        try:
            # Create event publisher
            publisher = EventPublisher(self.db_session)

            # Prepare event data
            event_data = {
                "application_id": application.application_id,
                "job_id": application.job_id,
                "employee_id": application.employee_id,
                "employee_email": application.employee_email,
                "employee_username": application.employee_username,
                "employer_id": employer_id,
                "cv_url": application.cv_url,
                "portfolio_url": application.portfolio_url,
                "status": application.status.value,
                "accepted_at": application.updated_at.isoformat() if application.updated_at else None
            }

            # Publish event
            publisher.publish_event(
                event_type="ApplicationAccepted",
                aggregate_id=application.application_id,
                aggregate_type="JobApplication",
                event_data=event_data,
                user_id=employer_id
            )

        except Exception as e:
            from flask import current_app
            current_app.logger.error(f"❌ Failed to publish ApplicationAccepted event: {e}")
            # Don't raise - application update already succeeded
            # Event can be retried from event store if needed

    def handle_delete_application(self, command: DeleteApplicationCommand) -> bool:
        """
        Handle DeleteApplicationCommand.
        Deletes an application.
        """
        return self.service.delete_application(
            application_id=command.application_id,
            employer_id=command.employer_id
        )
