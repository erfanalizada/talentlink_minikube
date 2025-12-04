"""
Repository layer for data access.
Single Responsibility: Handles database operations only (CRUD).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from models import Job, JobApplication, ApplicationStatus


class IJobRepository(ABC):
    """Interface for job repository."""

    @abstractmethod
    def create(self, job: Job) -> Job:
        pass

    @abstractmethod
    def get_by_id(self, job_id: int) -> Optional[Job]:
        pass

    @abstractmethod
    def get_all(self) -> List[Job]:
        pass

    @abstractmethod
    def get_by_employer(self, employer_id: str) -> List[Job]:
        pass

    @abstractmethod
    def update(self, job: Job) -> Job:
        pass

    @abstractmethod
    def delete(self, job_id: int) -> bool:
        pass


class JobRepository(IJobRepository):
    """Concrete implementation of job repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: int) -> Optional[Job]:
        return self.db.query(Job).filter(Job.job_id == job_id).first()

    def get_all(self) -> List[Job]:
        return self.db.query(Job).order_by(Job.created_at.desc()).all()

    def get_by_employer(self, employer_id: str) -> List[Job]:
        return self.db.query(Job).filter(Job.employer_id == employer_id).order_by(Job.created_at.desc()).all()

    def update(self, job: Job) -> Job:
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job_id: int) -> bool:
        job = self.get_by_id(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False


class IJobApplicationRepository(ABC):
    """Interface for job application repository."""

    @abstractmethod
    def create(self, application: JobApplication) -> JobApplication:
        pass

    @abstractmethod
    def get_by_id(self, application_id: int) -> Optional[JobApplication]:
        pass

    @abstractmethod
    def get_by_job(self, job_id: int) -> List[JobApplication]:
        pass

    @abstractmethod
    def get_by_employee(self, employee_id: str) -> List[JobApplication]:
        pass

    @abstractmethod
    def update(self, application: JobApplication) -> JobApplication:
        pass

    @abstractmethod
    def delete(self, application_id: int) -> bool:
        pass


class JobApplicationRepository(IJobApplicationRepository):
    """Concrete implementation of job application repository."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, application: JobApplication) -> JobApplication:
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_by_id(self, application_id: int) -> Optional[JobApplication]:
        return self.db.query(JobApplication).filter(JobApplication.application_id == application_id).first()

    def get_by_job(self, job_id: int) -> List[JobApplication]:
        return self.db.query(JobApplication).filter(JobApplication.job_id == job_id).order_by(JobApplication.created_at.desc()).all()

    def get_by_employee(self, employee_id: str) -> List[JobApplication]:
        return self.db.query(JobApplication).filter(JobApplication.employee_id == employee_id).order_by(JobApplication.created_at.desc()).all()

    def update(self, application: JobApplication) -> JobApplication:
        self.db.commit()
        self.db.refresh(application)
        return application

    def delete(self, application_id: int) -> bool:
        application = self.get_by_id(application_id)
        if application:
            self.db.delete(application)
            self.db.commit()
            return True
        return False
