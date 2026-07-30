import uuid
from typing import Any, Dict, Optional
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class Job(Base):
    """Core-HR Canonical Job Profile model."""
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(50), unique=True, index=True, nullable=False, doc="Unique Job Code e.g. JOB-101")
    job_title = Column(String(100), unique=True, nullable=False, doc="Job Title e.g. Senior Design Engineer")
    job_family = Column(String(100), nullable=True, doc="Job Family e.g. Design, Engineering, Product")
    job_level = Column(String(50), nullable=True, doc="Job Seniority Grade e.g. L5 Senior, L6 Lead")
    job_description = Column(Text, nullable=True, doc="Detailed Job Description")

    # Relationships
    users = relationship("User", back_populates="job_rel")
    competencies = relationship("Competency", back_populates="job_rel", cascade="all, delete-orphan", lazy="joined")


class Competency(Base):
    """Linked Competencies table for Jobs."""
    __tablename__ = "competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    competency_id = Column(String(50), unique=True, index=True, nullable=False, doc="Unique Competency ID e.g. COMP-101")
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, doc="FK to jobs.id")
    name = Column(String(100), nullable=False, doc="Competency Name e.g. Technical Execution")
    category = Column(String(100), nullable=True, doc="Category e.g. Core Technical, Leadership")
    target_rating = Column(Float, default=4.0, nullable=True, doc="Target rating score e.g. 4.5")
    description = Column(Text, nullable=True)

    # Relationships
    job_rel = relationship("Job", back_populates="competencies")


class Department(Base):
    """Core-HR Canonical Department / Business Unit model."""
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    department_id = Column(String(50), unique=True, index=True, nullable=False, doc="Department Code e.g. DEPT-101")
    name = Column(String(100), unique=True, nullable=False, doc="Department Name e.g. Engineering")
    cost_center_code = Column(String(50), nullable=True, doc="Financial Cost Center Code e.g. CC-4001")
    description = Column(Text, nullable=True)

    # Relationships
    users = relationship("User", back_populates="department_rel")


class User(Base):
    """Core-HR Canonical Worker / Employee domain model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(50), unique=True, index=True, nullable=True, doc="Core-HR Employee Number e.g. EMP-1001")
    first_name = Column(String(100), nullable=True, doc="Given Name")
    last_name = Column(String(100), nullable=True, doc="Family / Surname")
    email = Column(String(255), unique=True, index=True, nullable=False, doc="Work Email")

    @property
    def full_name(self) -> str:
        fname = self.first_name or ''
        lname = self.last_name or ''
        combined = f"{fname} {lname}".strip()
        return combined if combined else (self.email.split('@')[0] if self.email else '')

    @full_name.setter
    def full_name(self, value: str):
        if value and not self.first_name and not self.last_name:
            parts = value.split(' ', 1)
            self.first_name = parts[0]
            if len(parts) > 1:
                self.last_name = parts[1]

    dob = Column(String(20), nullable=True, doc="Date of Birth YYYY-MM-DD")
    doh = Column(String(20), nullable=True, doc="Date of Hire YYYY-MM-DD")
    employment_status = Column(String(50), default="ACTIVE", nullable=False, doc="ACTIVE, PROBATION, LEAVE, TERMINATED")
    employment_type = Column(String(50), default="FULL_TIME", nullable=False, doc="FULL_TIME, PART_TIME, CONTRACTOR, INTERN")
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=True, doc="FK to jobs.id")
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True, doc="FK to departments.id")
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True, doc="FK to manager user.id")

    # Relationships
    job_rel = relationship("Job", back_populates="users", lazy="joined")
    department_rel = relationship("Department", back_populates="users", lazy="joined")

    @property
    def job_title(self) -> str:
        return self.job_rel.job_title if self.job_rel else "Employee"

    @property
    def role(self) -> str:
        return self.job_title

    @property
    def department(self) -> Optional[str]:
        return self.department_rel.name if self.department_rel else None

    # Address & Social Profile Fields
    country = Column(String(100), nullable=True)
    city_state = Column(String(150), nullable=True)
    postal_code = Column(String(50), nullable=True)
    tax_id = Column(String(50), nullable=True)
    photo_url = Column(Text, nullable=True)

    facebook = Column(Text, nullable=True)
    x_link = Column(Text, nullable=True)
    linkedin = Column(Text, nullable=True)
    instagram = Column(Text, nullable=True)

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")

    # Relationships
    reviews = relationship("PerformanceReview", foreign_keys="PerformanceReview.employee_id", back_populates="employee")
    metrics = relationship("Metric", back_populates="employee")
    employment_records = relationship("WorkerEmployment", back_populates="person_rel")


class WorkerEmployment(Base):
    """Core-HR Canonical Worker Employment model."""
    __tablename__ = "worker_employment"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worker_id = Column(String(50), unique=True, index=True, nullable=False, doc="Unique Worker Employment ID e.g. WRK-1001")
    person_id = Column(String(36), ForeignKey("users.id"), nullable=False, doc="FK to users.id (Person)")
    hire_date = Column(String(20), nullable=False, doc="Date of Hire YYYY-MM-DD")
    termination_date = Column(String(20), nullable=True, doc="Date of Termination YYYY-MM-DD")
    employment_type = Column(String(50), default="FULL_TIME", nullable=False, doc="FULL_TIME (FT), PART_TIME (PT), CONTRACTOR")
    work_authorization = Column(String(100), default="US_CITIZEN", nullable=True, doc="Work Authorization e.g. US_CITIZEN, H1B_VISA, EAD")
    union_status = Column(String(50), default="NON_UNION", nullable=True, doc="Union Status e.g. NON_UNION, UNION_MEMBER")
    flsa_status = Column(String(50), default="EXEMPT", nullable=True, doc="FLSA Status e.g. EXEMPT, NON_EXEMPT")

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")

    # Relationships
    person_rel = relationship("User", back_populates="employment_records", lazy="joined")


class Metric(Base):
    """Cognitive & Performance Metric model."""
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    metric_type = Column(String(100), nullable=False, index=True, doc="Type of metric e.g., problem_solving, velocity, focus_score")
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    category = Column(String(100), nullable=True, doc="Cognitive, Behavioral, Productivity")
    notes = Column(Text, nullable=True)

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")

    # Relationships
    employee = relationship("User", back_populates="metrics")


class PerformanceReview(Base):
    """Core-HR Performance Review entity."""
    __tablename__ = "performance_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    review_cycle = Column(String(50), nullable=True, doc="Review Cycle e.g. Q2 2026, Annual 2026")
    period = Column(String(50), nullable=True, doc="e.g. Q2 2026")

    # Core-HR Performance Fields
    goals = Column(JSON, default=list, nullable=True, doc="Goals objectives & accomplishment tracking")
    competency_ratings = Column(JSON, default=dict, nullable=True, doc="Competency rating scores by dimension")
    manager_review = Column(Text, nullable=True, doc="Manager evaluation notes & feedback")
    self_review = Column(Text, nullable=True, doc="Employee self-evaluation notes")
    calibration_scores = Column(Float, nullable=True, doc="Final calibrated overall performance score")

    status = Column(String(50), default="COMPLETED", nullable=False, doc="DRAFT, SELF_REVIEW, MANAGER_REVIEW, IN_CALIBRATION, COMPLETED")
    overall_rating = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")

    # Relationships
    employee = relationship("User", foreign_keys=[employee_id], back_populates="reviews")


class Goal(Base):
    """Goal & KPI tracking model."""
    __tablename__ = "goals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, default=0.0)
    status = Column(String(50), default="in_progress", nullable=False)

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")


class EventTransaction(Base):
    """Event Transactions domain model."""
    __tablename__ = "event_transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(50), unique=True, index=True, nullable=False, doc="Unique Event ID e.g. EVT-1001")
    event_name = Column(String(150), nullable=False, doc="Event transaction name e.g. HIRE_EVENT, PROMOTION, TRANSFER")
    event_date = Column(String(20), nullable=False, doc="Date of transaction event YYYY-MM-DD")
    person_id = Column(String(36), ForeignKey("users.id"), nullable=True, doc="FK to users.id")
    description = Column(Text, nullable=True, doc="Event details or transaction notes")

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")

    # Relationships
    person_rel = relationship("User", lazy="joined")
