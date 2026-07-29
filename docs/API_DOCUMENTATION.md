# Cognitive Metrics AI Backend API Documentation & Integration Guide

Welcome to the **Cognitive Metrics AI Backend API** documentation. This guide details every REST API endpoint, its purpose, expected payloads, response formats, and how enterprise clients can integrate the API with their own custom database schemas.

---

## Architecture & Enterprise Integration Model

### How Businesses Connect Their Database Schemas

`CognitiveMetricsAI_BE` provides 3 primary integration mechanisms for connecting enterprise database schemas:

1. **Direct Connection String Override (`DATABASE_URL`)**:
   Point `DATABASE_URL` in `.env` to your enterprise database (PostgreSQL, MySQL, SQL Server, SQLite).
   Example: `DATABASE_URL="postgresql+asyncpg://user:pass@dbhost:5432/enterprise_db"`

2. **Custom Enterprise Metadata (`custom_metadata`)**:
   Every entity (`User`, `Metric`, `PerformanceReview`, `Goal`) supports a `custom_metadata` JSON field. Businesses can pass arbitrary internal fields (e.g. `employee_hr_id`, `cost_center`, `security_clearance`, `custom_rubric_scores`) without performing SQL migrations.

3. **Repository Adapter Pattern**:
   If an enterprise has existing legacy tables, developers can write a custom subclass of `BaseRepository` in `app/repositories/` to map existing SQL views or tables directly to CognitiveMetricsAI entities without changing frontend or API logic.

---

## API Summary & Endpoints Overview

| Method | Endpoint | Description | Purpose |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root Welcome & Docs | Returns link to interactive Swagger & ReDoc documentation. |
| `GET` | `/api/v1/health` | Health Check | Verifies backend service status and database connectivity. |
| `POST` | `/api/v1/users/` | Create User | Registers a new employee or manager entity with enterprise metadata. |
| `GET` | `/api/v1/users/` | List Users | Retrieves paginated users with optional role and department filters. |
| `GET` | `/api/v1/users/{user_id}` | Get User | Fetches complete user details and custom enterprise attributes. |
| `POST` | `/api/v1/metrics/` | Record Metric | Logs cognitive performance, productivity, or problem-solving metrics. |
| `GET` | `/api/v1/metrics/` | Query Metrics | Filters logged metrics by employee UUID, metric type, or category. |
| `GET` | `/api/v1/metrics/{metric_id}` | Get Metric | Retrieves details for a specific recorded metric entry. |
| `POST` | `/api/v1/reviews/` | Submit Review | Submits a performance evaluation review record. |
| `GET` | `/api/v1/reviews/` | List Reviews | Queries reviews by employee, reviewer, period, or status. |
| `GET` | `/api/v1/reviews/{review_id}` | Get Review | Retrieves feedback and rating details for a review record. |

---

## Endpoint Details

### 1. User & Employee Management (`/api/v1/users`)

#### `POST /api/v1/users/`
- **Purpose**: Creates an employee profile or manager account in the system.
- **Request Body**:
  ```json
  {
    "email": "jane.doe@company.com",
    "full_name": "Jane Doe",
    "role": "manager",
    "department": "Engineering",
    "manager_id": null,
    "custom_metadata": {
      "enterprise_employee_id": "EMP-90210",
      "cost_center": "ENG-US-EAST",
      "location": "New York"
    }
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": "3a7b6c5d-1234-5678-90ab-cdef12345678",
    "email": "jane.doe@company.com",
    "full_name": "Jane Doe",
    "role": "manager",
    "department": "Engineering",
    "manager_id": null,
    "custom_metadata": {
      "enterprise_employee_id": "EMP-90210",
      "cost_center": "ENG-US-EAST",
      "location": "New York"
    },
    "is_active": true,
    "created_at": "2026-07-29T12:00:00Z",
    "updated_at": "2026-07-29T12:00:00Z"
  }
  ```

---

### 2. Cognitive Metrics API (`/api/v1/metrics`)

#### `POST /api/v1/metrics/`
- **Purpose**: Logs cognitive, behavioral, or productivity metrics measured for an employee over time.
- **Request Body**:
  ```json
  {
    "employee_id": "3a7b6c5d-1234-5678-90ab-cdef12345678",
    "metric_type": "problem_solving",
    "value": 88.5,
    "unit": "score",
    "category": "Cognitive",
    "notes": "Demonstrated outstanding algorithmic reasoning during Q1 initiative",
    "custom_metadata": {
      "project_code": "PROJ-ALPHA",
      "evaluator_system": "InternalAI-V2"
    }
  }
  ```

#### `GET /api/v1/metrics/?employee_id={id}&metric_type={type}`
- **Purpose**: Fetches historical metrics to power Vue dashboard charts (`ApexCharts`) in `CognitiveMetricsAI_FE`.

---

### 3. Performance Reviews API (`/api/v1/reviews`)

#### `POST /api/v1/reviews/`
- **Purpose**: Records a structured performance evaluation review.
- **Request Body**:
  ```json
  {
    "employee_id": "3a7b6c5d-1234-5678-90ab-cdef12345678",
    "reviewer_id": "8f9e0d1c-5678-1234-abcd-ef1234567890",
    "period": "Q1 2026",
    "status": "approved",
    "overall_rating": 4.8,
    "feedback": "Exceptional team leadership and problem solving skills.",
    "custom_metadata": {
      "promotion_recommended": true,
      "salary_grade": "L6"
    }
  }
  ```

---

## Interactive OpenAPI Documentation

When running `CognitiveMetricsAI_BE`, interactive API documentation with live testing is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
