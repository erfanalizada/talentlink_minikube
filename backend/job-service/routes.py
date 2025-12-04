"""
Routes layer for HTTP endpoints.
Single Responsibility: Handles HTTP request/response mapping.
"""
from flask import Blueprint, request, jsonify, send_from_directory
from database import SessionLocal
from repositories import JobRepository, JobApplicationRepository
from services import JobService, JobApplicationService

jobs_bp = Blueprint('jobs', __name__)


def get_job_service():
    """Factory function for job service."""
    db = SessionLocal()
    repository = JobRepository(db)
    return JobService(repository), db


def get_application_service():
    """Factory function for application service."""
    db = SessionLocal()
    job_repository = JobRepository(db)
    app_repository = JobApplicationRepository(db)
    return JobApplicationService(app_repository, job_repository), db


# Job endpoints

@jobs_bp.route("/api/jobs", methods=["POST"])
def create_job():
    """Create a new job posting (Employer only)."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")
        title = data.get("title")
        description = data.get("description")
        salary = data.get("salary")
        skills = data.get("skills", [])

        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400

        service, db = get_job_service()
        try:
            job = service.create_job(employer_id, title, description, salary, skills)
            return jsonify(job.to_dict()), 201
        finally:
            db.close()

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500


@jobs_bp.route("/api/jobs", methods=["GET"])
def get_all_jobs():
    """Get all job postings (Public)."""
    try:
        service, db = get_job_service()
        try:
            jobs = service.get_all_jobs()
            return jsonify([job.to_dict() for job in jobs]), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch jobs: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    """Get a specific job by ID."""
    try:
        service, db = get_job_service()
        try:
            job = service.get_job(job_id)
            if not job:
                return jsonify({"error": "Job not found"}), 404
            return jsonify(job.to_dict()), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch job: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/employer/<employer_id>", methods=["GET"])
def get_jobs_by_employer(employer_id):
    """Get all jobs posted by a specific employer."""
    try:
        service, db = get_job_service()
        try:
            jobs = service.get_jobs_by_employer(employer_id)
            return jsonify([job.to_dict() for job in jobs]), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch jobs: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>", methods=["PUT", "PATCH"])
def update_job(job_id):
    """Update a job posting (Owner only)."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")

        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400

        service, db = get_job_service()
        try:
            job = service.update_job(
                job_id,
                employer_id,
                title=data.get("title"),
                description=data.get("description"),
                salary=data.get("salary"),
                skills=data.get("skills")
            )
            if not job:
                return jsonify({"error": "Job not found"}), 404
            return jsonify(job.to_dict()), 200
        finally:
            db.close()

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update job: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    """Delete a job posting (Owner only)."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")

        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400

        service, db = get_job_service()
        try:
            success = service.delete_job(job_id, employer_id)
            if not success:
                return jsonify({"error": "Job not found"}), 404
            return jsonify({"message": "Job deleted successfully"}), 200
        finally:
            db.close()

    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500


# Application endpoints

@jobs_bp.route("/api/jobs/<int:job_id>/apply", methods=["POST"])
def apply_to_job(job_id):
    """Apply to a job (Employee only)."""
    try:
        data = request.get_json()
        employee_id = data.get("employee_id")
        cv_base64 = data.get("cv")
        portfolio_url = data.get("portfolio_url")

        if not employee_id:
            return jsonify({"error": "employee_id is required"}), 400
        if not cv_base64:
            return jsonify({"error": "cv is required"}), 400

        service, db = get_application_service()
        try:
            application = service.create_application(job_id, employee_id, cv_base64, portfolio_url)
            return jsonify(application.to_dict()), 201
        finally:
            db.close()

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to submit application: {str(e)}"}), 500


@jobs_bp.route("/api/jobs/<int:job_id>/applications", methods=["GET"])
def get_job_applications(job_id):
    """Get all applications for a specific job (Employer only)."""
    try:
        employer_id = request.args.get("employer_id")
        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400

        service, db = get_application_service()
        try:
            applications = service.get_applications_by_job(job_id, employer_id)
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
    """Get all applications submitted by an employee."""
    try:
        service, db = get_application_service()
        try:
            applications = service.get_applications_by_employee(employee_id)
            return jsonify([app.to_dict() for app in applications]), 200
        finally:
            db.close()
    except Exception as e:
        return jsonify({"error": f"Failed to fetch applications: {str(e)}"}), 500


@jobs_bp.route("/api/applications/<int:application_id>/status", methods=["PUT", "PATCH"])
def update_application_status(application_id):
    """Update the status of an application (Employer only)."""
    try:
        data = request.get_json()
        employer_id = data.get("employer_id")
        status = data.get("status")

        if not employer_id:
            return jsonify({"error": "employer_id is required"}), 400
        if not status:
            return jsonify({"error": "status is required"}), 400

        service, db = get_application_service()
        try:
            application = service.update_application_status(application_id, employer_id, status)
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
