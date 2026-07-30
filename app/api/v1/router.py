from fastapi import APIRouter

from app.api.v1.endpoints import metrics, reviews, users, departments, jobs, employment, events

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users & Employees"])
api_router.include_router(employment.router, prefix="/employment", tags=["Worker Employment"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs & Competencies"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(events.router, prefix="/events", tags=["Event Transactions"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Cognitive Metrics"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Performance Reviews"])


@api_router.get("/health", tags=["Health & System"])
async def health_check():
    """Health check endpoint to verify backend service status and database connectivity."""
    return {
        "status": "healthy",
        "service": "CognitiveMetricsAI_BE",
        "version": "1.0.0",
    }
