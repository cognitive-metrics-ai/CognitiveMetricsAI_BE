import uuid
from typing import Any, Dict, Optional
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User / Employee domain model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="employee", nullable=False)
    department = Column(String(100), nullable=True)
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Enterprise dynamic custom fields schema
    custom_metadata = Column(JSON, default=dict, nullable=False, doc="Enterprise custom key-value metadata")

    # Relationships
    reviews = relationship("PerformanceReview", foreign_keys="PerformanceReview.employee_id", back_populates="employee")
    metrics = relationship("Metric", back_populates="employee")


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
    """Performance Review entity."""
    __tablename__ = "performance_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    period = Column(String(50), nullable=False, doc="e.g., Q1 2026, H2 2025")
    status = Column(String(50), default="draft", nullable=False, doc="draft, submitted, approved")
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
