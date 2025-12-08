"""
Routes layer for HTTP endpoints.
Single Responsibility: Handles HTTP request/response mapping.
Uses CQRS pattern to separate read (queries) from write (commands) operations.
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.exceptions import BadRequest
from werkzeug.utils import secure_filename
import os
from database import SessionLocal
from repositories import JobRepository, JobApplicationRepository
from services import JobService, JobApplicationService
from cqrs.handlers import JobCommandHandler, ApplicationCommandHandler, JobQueryHandler, ApplicationQueryHandler
from cqrs.commands import CreateJobCommand, UpdateJobCommand, DeleteJobCommand, ApplyToJobCommand, UpdateApplicationStatusCommand, DeleteApplicationCommand
from cqrs.queries import GetAllJobsQuery, GetJobByIdQuery, GetJobsByEmployerQuery, GetAllJobsWithApplicationStatusQuery, GetApplicationsByJobQuery, GetApplicationsByEmployeeQuery

jobs_bp = Blueprint('jobs', __name__)


def get_job_handlers():
    """Factory function for job CQRS handlers."""
    db = SessionLocal()
    repository = JobRepository(db)
    service = JobService(repository)
    command_handler = JobCommandHandler(service)
    query_handler = JobQueryHandler(service)
    return command_handler, query_handler, db


def get_application_handlers():
    """Factory function for application CQRS handlers."""
    db = SessionLocal()
    job_repository = JobRepository(db)
    app_repository = JobApplicationRepository(db)
    service = JobApplicationService(app_repository, job_repository)
    command_handler = ApplicationCommandHandler(service, db_session=db)
    query_handler = ApplicationQueryHandler(service)
    return command_handler, query_handler, db


# Job endpoints

@jobs_bp.route("/api/jobs", methods=["POST"])
def create_job():
    """Create a new job posting (Employer only) - COMMAND."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")

        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400

        # Create command
        command = CreateJobCommand(
            employer_id=employer_id,
            title=data.get("title"),
            description=data.get("description"),
            salary=data.get("salary"),
            skills=data.get("skills", [])
        )

        # Execute command
        command_handler, _, db = get_job_handlers()
        try:
            job = command_handler.handle_create_job(command)
            return jsonify(job.to_dict()), 201
        finally:
            db.close()

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500


@jobs_bp.route("/api/jobs", methods=["GET"])
def get_all_jobs():
    """
    Get all job postings (Public) - QUERY.
    Optional query parameter: employee_id - if provided, includes has_applied flag
    """
    try:
        employee_id = request.args.get("employee_id")

        _, query_handler, db = get_job_handlers()
        try:
            if employee_id:
                # Query with application status for employee
                query = GetAllJobsWithApplicationStatusQuery(employee_id=employee_id)
                jobs_with_status = query_handler.handle_get_all_jobs_with_application_status(query)
                return jsonify(jobs_with_status), 200
            else:
                # Query all jobs
                query = GetAllJobsQuery()
                jobs = query_handler.handle_get_all_jobs(query)
                return jsonify([job.to_dict() for job in jobs]), 200
        finally:
            db.close()
    except Exception as e:
        current_app.logger.error(f"Failed to fetch jobs: {e}")
        return jsonify({"error": f"Failed to fetch jobs: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    """
    Get a specific job by ID - QUERY.
    Optional query parameter: employee_id - if provided, includes has_applied flag
    """
    try:
        employee_id = request.args.get("employee_id")

        _, query_handler, db = get_job_handlers()
        try:
            # Execute query
            query = GetJobByIdQuery(job_id=job_id, employee_id=employee_id)
            job = query_handler.handle_get_job_by_id(query)

            if not job:
                return jsonify({"error": "Job not found"}), 404

            job_dict = job.to_dict()

            # Add has_applied flag if employee_id is provided
            if employee_id:
                from repositories import JobApplicationRepository
                app_repo = JobApplicationRepository(db)
                employee_applications = app_repo.get_by_employee(employee_id)
                applied_job_ids = {app.job_id for app in employee_applications}
                job_dict["has_applied"] = job_id in applied_job_ids

            return jsonify(job_dict), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch job: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/employer/<employer_id>", methods=["GET"])
def get_jobs_by_employer(employer_id):
    """Get all jobs posted by a specific employer - QUERY."""
    try:
        _, query_handler, db = get_job_handlers()
        try:
            # Execute query
            query = GetJobsByEmployerQuery(employer_id=employer_id)
            jobs = query_handler.handle_get_jobs_by_employer(query)
            return jsonify([job.to_dict() for job in jobs]), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch jobs: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>", methods=["PUT", "PATCH"])
def update_job(job_id):
    """Update a job posting (Owner only) - COMMAND."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")

        if not employer_id:
            current_app.logger.warning(f"Update job {job_id} failed: employer_id missing")
            return jsonify({"error": "employer_id is required"}), 400

        current_app.logger.info(f"Updating job {job_id} by employer {employer_id}")

        # Create command
        command = UpdateJobCommand(
            job_id=job_id,
            employer_id=employer_id,
            title=data.get("title"),
            description=data.get("description"),
            salary=data.get("salary"),
            skills=data.get("skills")
        )

        # Execute command
        command_handler, _, db = get_job_handlers()
        try:
            job = command_handler.handle_update_job(command)
            if not job:
                current_app.logger.warning(f"Job {job_id} not found for update")
                return jsonify({"error": "Job not found"}), 404

            current_app.logger.info(f"✅ Job {job_id} updated successfully")
            return jsonify(job.to_dict()), 200
        finally:
            db.close()

    except PermissionError as e:
        current_app.logger.warning(f"Permission denied updating job {job_id}: {e}")
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        current_app.logger.warning(f"Validation error updating job {job_id}: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"❌ Failed to update job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to update job: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    """Delete a job posting (Owner only) - COMMAND."""
    try:
        data = request.get_json() if request.data else {}
        employer_id = data.get("employer_id")

        if not employer_id:
            current_app.logger.warning(f"Delete job {job_id} failed: employer_id missing")
            return jsonify({"error": "employer_id is required"}), 400

        current_app.logger.info(f"Deleting job {job_id} by employer {employer_id}")

        # Create command
        command = DeleteJobCommand(job_id=job_id, employer_id=employer_id)

        # Execute command
        command_handler, _, db = get_job_handlers()
        try:
            success = command_handler.handle_delete_job(command)
            if not success:
                current_app.logger.warning(f"Job {job_id} not found for deletion")
                return jsonify({"error": "Job not found"}), 404

            current_app.logger.info(f"✅ Job {job_id} deleted successfully")
            return jsonify({"message": "Job deleted successfully"}), 200
        finally:
            db.close()

    except PermissionError as e:
        current_app.logger.warning(f"Permission denied deleting job {job_id}: {e}")
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"❌ Failed to delete job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500


# Application endpoints

@jobs_bp.route("/api/jobs/<int:job_id>/apply", methods=["POST"])
def apply_to_job(job_id):
    """Apply to a job (Employee only) - COMMAND."""
    try:
        # Support both JSON (base64 CV) and multipart/form-data (file upload)
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            # Form-based upload
            employee_id = request.form.get('employee_id')
            cv_file = request.files.get('cv')
            portfolio_url = request.form.get('portfolio_url')

            current_app.logger.info(f"Multipart apply request to /api/jobs/{job_id}/apply - employee_id: {employee_id}, cv_file: {getattr(cv_file, 'filename', None)}, portfolio_url_present: {bool(portfolio_url)}")

            if not employee_id:
                return jsonify({"error": "employee_id is required"}), 400
            if not cv_file:
                return jsonify({"error": "cv file is required"}), 400

            # Save uploaded file to uploads directory
            upload_dir = "/app/uploads/cvs"
            os.makedirs(upload_dir, exist_ok=True)
            filename = secure_filename(f"{employee_id}_{job_id}_{cv_file.filename}")
            filepath = os.path.join(upload_dir, filename)
            cv_file.save(filepath)
            cv_url = f"/api/jobs/uploads/cvs/{filename}"

            # Create command
            command = ApplyToJobCommand(
                job_id=job_id,
                employee_id=employee_id,
                cv_base64=None,
                portfolio_url=portfolio_url,
                cv_url=cv_url
            )

            # Execute command
            command_handler, _, db = get_application_handlers()
            try:
                application = command_handler.handle_apply_to_job(command)
                return jsonify(application.to_dict()), 201
            finally:
                db.close()
        else:
            # JSON-based upload (existing behavior)
            try:
                data = request.get_json()
            except BadRequest as e:
                current_app.logger.error(f"Invalid JSON in request to /api/jobs/{job_id}/apply: {e}")
                return jsonify({"error": f"Invalid JSON payload: {str(e)}"}), 400

            if not data:
                current_app.logger.error(f"Empty JSON payload in request to /api/jobs/{job_id}/apply")
                return jsonify({"error": "Invalid or empty JSON payload"}), 400

            # Log minimal info about payload to help debugging (avoid printing full base64)
            try:
                cv_len = len(data.get("cv", "")) if data.get("cv") else 0
            except Exception:
                cv_len = 0
            current_app.logger.info(f"JSON apply request to /api/jobs/{job_id}/apply - employee_id: {data.get('employee_id')}, cv_len: {cv_len}, portfolio_url_present: {bool(data.get('portfolio_url'))}")

            employee_id = data.get("employee_id")
            cv_base64 = data.get("cv")
            portfolio_url = data.get("portfolio_url")

            if not employee_id:
                return jsonify({"error": "employee_id is required"}), 400
            if not cv_base64:
                return jsonify({"error": "cv is required"}), 400

            # Create command
            command = ApplyToJobCommand(
                job_id=job_id,
                employee_id=employee_id,
                cv_base64=cv_base64,
                portfolio_url=portfolio_url,
                cv_url=None
            )

            # Execute command
            command_handler, _, db = get_application_handlers()
            try:
                application = command_handler.handle_apply_to_job(command)
                return jsonify(application.to_dict()), 201
            finally:
                db.close()

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to submit application: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>/applications", methods=["GET"])
def get_job_applications(job_id):
    """Get all applications for a specific job (Employer only) - QUERY."""
    try:
        employer_id = request.args.get("employer_id")
        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400

        # Execute query
        query = GetApplicationsByJobQuery(job_id=job_id, employer_id=employer_id)
        _, query_handler, db = get_application_handlers()
        try:
            applications = query_handler.handle_get_applications_by_job(query)
            return jsonify([app.to_dict() for app in applications]), 200
        finally:
            db.close()

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to fetch applications: {str(e)}"}), 500


@jobs_bp.route("/api/applications/employee/<employee_id>", methods=["GET"])
def get_employee_applications(employee_id):
    """Get all applications submitted by an employee - QUERY."""
    try:
        # Execute query
        query = GetApplicationsByEmployeeQuery(employee_id=employee_id)
        _, query_handler, db = get_application_handlers()
        try:
            applications = query_handler.handle_get_applications_by_employee(query)
            return jsonify([app.to_dict() for app in applications]), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch applications: {str(e)}"}), 500


@jobs_bp.route("/api/applications/<int:application_id>/status", methods=["PUT", "PATCH"])
def update_application_status(application_id):
    """Update the status of an application (Employer only) - COMMAND."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")
        status = data.get("status")

        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400
        if not status:
            return jsonify({"error": "status is required"}), 400

        # Create command
        command = UpdateApplicationStatusCommand(
            application_id=application_id,
            employer_id=employer_id,
            status=status
        )

        # Execute command
        command_handler, _, db = get_application_handlers()
        try:
            application = command_handler.handle_update_application_status(command)
            if not application:
                return jsonify({"error": "Application not found"}), 404
            return jsonify(application.to_dict()), 200
        finally:
            db.close()

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update application: {str(e)}"}), 500


@jobs_bp.route("/api/applications/<int:application_id>", methods=["DELETE"])
def delete_application(application_id):
    """Delete an application (Employer only) - COMMAND."""
    try:
        data = request.get_json() if request.data else {}
        employer_id = data.get("employer_id")

        if not employer_id:
            current_app.logger.warning(f"Delete application {application_id} failed: employer_id missing")
            return jsonify({"error": "employer_id is required"}), 400

        current_app.logger.info(f"Deleting application {application_id} by employer {employer_id}")

        # Create command
        command = DeleteApplicationCommand(
            application_id=application_id,
            employer_id=employer_id
        )

        # Execute command
        command_handler, _, db = get_application_handlers()
        try:
            success = command_handler.handle_delete_application(command)
            if not success:
                current_app.logger.warning(f"Application {application_id} not found for deletion")
                return jsonify({"error": "Application not found"}), 404

            current_app.logger.info(f"✅ Application {application_id} deleted successfully")
            return jsonify({"message": "Application deleted successfully"}), 200
        finally:
            db.close()

    except PermissionError as e:
        current_app.logger.warning(f"Permission denied deleting application {application_id}: {e}")
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"❌ Failed to delete application {application_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to delete application: {str(e)}"}), 500


# File serving

@jobs_bp.route("/api/jobs/uploads/cvs/<filename>", methods=["GET"])
def serve_cv(filename):
    """Serve uploaded CV files."""
    try:
        return send_from_directory("/app/uploads/cvs", filename)
    except Exception as e:
        return jsonify({"error": f"File not found: {str(e)}"}), 404


# Health check

@jobs_bp.route("/api/jobs/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "job-service ok"}), 200
