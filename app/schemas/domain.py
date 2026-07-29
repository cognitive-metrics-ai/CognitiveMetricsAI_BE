from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Unique email address of the user/employee")
    full_name: str = Field(..., description="Full display name")
    role: str = Field("employee", description="Role within the organization (e.g. employee, manager, admin)")
    department: Optional[str] = Field(None, description="Department or business unit")
    manager_id: Optional[str] = Field(None, description="UUID of manager user")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom enterprise schema fields")


class UserCreate(UserBase):
    pass


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


# --- Performance Review Schemas ---
class ReviewBase(BaseModel):
    employee_id: str = Field(..., description="UUID of employee receiving the performance review")
    reviewer_id: str = Field(..., description="UUID of reviewer/manager performing the review")
    period: str = Field(..., description="Review period identifier e.g. Q1 2026, H2 2025")
    status: str = Field("draft", description="Review lifecycle status (draft, submitted, approved)")
    overall_rating: Optional[float] = Field(None, description="Overall numerical rating (e.g. 1.0 to 5.0)")
    feedback: Optional[str] = Field(None, description="Detailed written review feedback")
    custom_metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom enterprise review schema attributes")


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
