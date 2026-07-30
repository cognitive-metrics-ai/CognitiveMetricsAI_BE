from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr, model_validator


# --- Competency Schemas (Linked Table to Jobs) ---
class CompetencyBase(BaseModel):
    competency_id: str = Field(..., description="Unique Competency ID e.g. COMP-101")
    name: str = Field(..., description="Competency name e.g. Technical Execution")
    category: Optional[str] = Field("Core Technical", description="Category e.g. Core Technical, Leadership")
    target_rating: Optional[float] = Field(4.0, description="Target rating e.g. 4.5")
    description: Optional[str] = Field(None, description="Detailed competency description")


class CompetencyCreate(CompetencyBase):
    job_id: str = Field(..., description="UUID of linked Job record")


class CompetencyResponse(CompetencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_id: str


# --- Job Schemas (Core-HR Jobs with Linked Competencies) ---
class JobBase(BaseModel):
    job_id: str = Field(..., description="Unique Job Code e.g. JOB-101")
    job_title: str = Field(..., description="Job Title e.g. Senior Design Engineer")
    job_family: Optional[str] = Field(None, description="Job Family e.g. Design, Engineering, Product")
    job_level: Optional[str] = Field(None, description="Job Seniority Grade e.g. L5 Senior, L6 Lead")
    job_description: Optional[str] = Field(None, description="Detailed Job Description")


class JobCreate(JobBase):
    competencies: Optional[List[CompetencyBase]] = Field(default_factory=list)


class JobUpdate(BaseModel):
    job_title: Optional[str] = None
    job_family: Optional[str] = None
    job_level: Optional[str] = None
    job_description: Optional[str] = None


class JobResponse(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    competencies: List[CompetencyResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


# --- Department Schemas (Core-HR Canonical Business Units) ---
class DepartmentBase(BaseModel):
    department_id: str = Field(..., description="Department Code e.g. DEPT-101")
    name: str = Field(..., description="Department name e.g. Engineering")
    cost_center_code: Optional[str] = Field(None, description="Financial Cost Center Code e.g. CC-4001")
    description: Optional[str] = Field(None, description="Department description")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    cost_center_code: Optional[str] = None
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


# --- User / Employee Schemas (Core-HR Canonical Workers) ---
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Work Email address")
    first_name: Optional[str] = Field(None, description="Given Name")
    last_name: Optional[str] = Field(None, description="Family Name")
    full_name: Optional[str] = Field(None, description="Derived concatenated full display name")
    employee_id: Optional[str] = Field(None, description="Core-HR Employee Number e.g. EMP-1001")
    dob: Optional[str] = Field(None, description="Date of Birth YYYY-MM-DD")
    doh: Optional[str] = Field(None, description="Date of Hire YYYY-MM-DD")
    employment_status: Optional[str] = Field("ACTIVE", description="ACTIVE, PROBATION, LEAVE, TERMINATED")
    employment_type: Optional[str] = Field("FULL_TIME", description="FULL_TIME, PART_TIME, CONTRACTOR, INTERN")
    phone: Optional[str] = Field(None, description="Primary Phone number")
    bio: Optional[str] = Field(None, description="Professional Bio")
    job_title: Optional[str] = Field(None, description="Job title")
    job_id: Optional[str] = Field(None, description="UUID of linked Job record")
    role: Optional[str] = Field(None, description="Role alias")
    role_id: Optional[str] = Field(None, description="Role ID alias")
    department: Optional[str] = Field(None, description="Department name")
    department_id: Optional[str] = Field(None, description="UUID of linked Department record")
    manager_id: Optional[str] = Field(None, description="UUID of manager user")

    country: Optional[str] = Field(None, description="Country")
    city_state: Optional[str] = Field(None, description="City/State")
    postal_code: Optional[str] = Field(None, description="Postal Code")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    photo_url: Optional[str] = Field(None, description="Profile photo URL")

    facebook: Optional[str] = Field(None, description="Facebook profile URL")
    x_link: Optional[str] = Field(None, description="X.com profile URL")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    instagram: Optional[str] = Field(None, description="Instagram profile URL")

    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom enterprise schema fields")

    @model_validator(mode="after")
    def compute_full_name(self) -> "UserBase":
        if not self.full_name or self.full_name.strip() == "":
            fname = self.first_name or ""
            lname = self.last_name or ""
            combined = f"{fname} {lname}".strip()
            self.full_name = combined if combined else self.email.split("@")[0]
        return self


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    email: EmailStr = Field(..., description="Unique email address of the user")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    employee_id: Optional[str] = None
    dob: Optional[str] = None
    doh: Optional[str] = None
    employment_status: Optional[str] = None
    employment_type: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    job_id: Optional[str] = None
    job_title: Optional[str] = None
    role: Optional[str] = None
    role_id: Optional[str] = None
    department: Optional[str] = None
    department_id: Optional[str] = None
    country: Optional[str] = None
    city_state: Optional[str] = None
    postal_code: Optional[str] = None
    tax_id: Optional[str] = None
    photo_url: Optional[str] = None
    facebook: Optional[str] = None
    x_link: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# --- Metric Schemas ---
class MetricBase(BaseModel):
    employee_id: str = Field(..., description="UUID of employee associated with this metric")
    metric_type: str = Field(..., description="Type identifier e.g. problem_solving, velocity, focus_score")
    value: float = Field(..., description="Measured numerical value")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g. %, score, hrs, points)")
    category: Optional[str] = Field(None, description="Category classification (e.g. Cognitive, Behavioral, Productivity)")
    notes: Optional[str] = Field(None, description="Contextual notes or observation comments")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom enterprise metric attributes")


class MetricCreate(MetricBase):
    pass


class MetricResponse(MetricBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


# --- Performance Review Schemas (Core-HR) ---
class ReviewBase(BaseModel):
    employee_id: str = Field(..., description="UUID or Employee ID of employee receiving the review")
    reviewer_id: Optional[str] = Field(None, description="UUID of reviewer/manager performing the review")
    review_cycle: Optional[str] = Field("Q2 2026", description="Review cycle (e.g. Q2 2026, Annual 2026)")
    period: Optional[str] = Field("Q2 2026", description="Review period identifier")

    goals: Optional[Any] = Field(default_factory=list, description="Goal objectives & accomplishments tracking")
    competency_ratings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Competency rating scores by dimension")
    manager_review: Optional[str] = Field(None, description="Manager evaluation notes & feedback")
    self_review: Optional[str] = Field(None, description="Employee self-evaluation notes")
    calibration_scores: Optional[float] = Field(None, description="Final calibrated overall performance score e.g. 4.5")

    status: str = Field("COMPLETED", description="Review status (DRAFT, SELF_REVIEW, MANAGER_REVIEW, IN_CALIBRATION, COMPLETED)")
    overall_rating: Optional[float] = Field(None, description="Overall rating score")
    feedback: Optional[str] = Field(None, description="Written review feedback")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom enterprise review attributes")


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    review_cycle: Optional[str] = None
    period: Optional[str] = None
    goals: Optional[Any] = None
    competency_ratings: Optional[Dict[str, Any]] = None
    manager_review: Optional[str] = None
    self_review: Optional[str] = None
    calibration_scores: Optional[float] = None
    status: Optional[str] = None
    overall_rating: Optional[float] = None
    feedback: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


# --- Worker Employment Schemas (Core-HR Canonical) ---
class WorkerEmploymentBase(BaseModel):
    worker_id: str = Field(..., description="Unique Worker Employment ID e.g. WRK-1001")
    person_id: str = Field(..., description="Foreign Key UUID linking to users.id (Person)")
    hire_date: str = Field(..., description="Date of Hire YYYY-MM-DD")
    termination_date: Optional[str] = Field(None, description="Date of Termination YYYY-MM-DD")
    employment_type: str = Field("FULL_TIME", description="FULL_TIME (FT), PART_TIME (PT), CONTRACTOR")
    work_authorization: Optional[str] = Field("US_CITIZEN", description="Work Authorization e.g. US_CITIZEN, H1B_VISA, EAD")
    union_status: Optional[str] = Field("NON_UNION", description="Union Status e.g. NON_UNION, UNION_MEMBER")
    flsa_status: Optional[str] = Field("EXEMPT", description="FLSA Status e.g. EXEMPT, NON_EXEMPT")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom employment schema attributes")


class WorkerEmploymentCreate(WorkerEmploymentBase):
    pass


class WorkerEmploymentUpdate(BaseModel):
    hire_date: Optional[str] = None
    termination_date: Optional[str] = None
    employment_type: Optional[str] = None
    work_authorization: Optional[str] = None
    union_status: Optional[str] = None
    flsa_status: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class WorkerEmploymentResponse(WorkerEmploymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


# --- Event Transaction Schemas ---
class EventTransactionBase(BaseModel):
    event_id: str = Field(..., description="Unique Event Transaction ID e.g. EVT-1001")
    event_name: str = Field(..., description="Event transaction name e.g. HIRE_EVENT, PROMOTION_EVENT, TRANSFER")
    event_date: str = Field(..., description="Date of transaction event YYYY-MM-DD")
    person_id: Optional[str] = Field(None, description="Optional Foreign Key UUID linking to users.id")
    description: Optional[str] = Field(None, description="Audit notes or event details")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom event metadata attributes")


class EventTransactionCreate(EventTransactionBase):
    pass


class EventTransactionUpdate(BaseModel):
    event_name: Optional[str] = None
    event_date: Optional[str] = None
    person_id: Optional[str] = None
    description: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class EventTransactionResponse(EventTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
