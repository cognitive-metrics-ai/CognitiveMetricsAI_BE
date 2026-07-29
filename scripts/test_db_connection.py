import asyncio
import sys
import os
import traceback

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.models.domain import User, Metric, PerformanceReview
from app.repositories.sqlalchemy_repo import SQLAlchemyRepository
from app.schemas.domain import UserCreate, MetricCreate, ReviewCreate


async def main():
    print("==================================================")
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    env_exists = os.path.exists(env_path)
    print(f" Checking .env file at: {env_path} -> {'EXISTS' if env_exists else 'NOT FOUND (using fallback default)'}")
    
    db_target = settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL
    print(f" Target Database: {db_target}")
    print("==================================================")

    try:
        # Step 1: Initialize Database Tables
        print("\n1. Initializing schema tables on database...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   [OK] Schema tables (users, metrics, performance_reviews, goals) created successfully.")

        # Step 2: Create Test User with Enterprise Custom Metadata
        async with AsyncSessionLocal() as session:
            user_repo = SQLAlchemyRepository(User, session)
            metric_repo = SQLAlchemyRepository(Metric, session)
            review_repo = SQLAlchemyRepository(PerformanceReview, session)

            print("\n2. Testing User Creation with Enterprise Custom Metadata...")
            test_email = "neon_test_user@company.com"
            existing = await user_repo.get_all(email=test_email)
            
            if not existing:
                user_data = UserCreate(
                    email=test_email,
                    full_name="Alex Mercer (Neon Test)",
                    role="manager",
                    department="AI Research",
                    custom_metadata={
                        "neon_db_connected": True,
                        "enterprise_id": "NEON-9901",
                        "security_level": "Tier-1"
                    }
                )
                user = await user_repo.create(user_data)
                print(f"   [OK] Created User ID: {user.id} ({user.email})")
            else:
                user = existing[0]
                print(f"   [INFO] User already exists with ID: {user.id}")

            # Step 3: Record a Test Metric
            print("\n3. Testing Metric Creation...")
            metric_data = MetricCreate(
                employee_id=user.id,
                metric_type="problem_solving_speed",
                value=94.2,
                unit="score",
                category="Cognitive",
                notes="Neon database integration test record",
                custom_metadata={"test_run": "Neon verification"}
            )
            metric = await metric_repo.create(metric_data)
            print(f"   [OK] Created Metric ID: {metric.id} - {metric.metric_type}: {metric.value} {metric.unit}")

            # Step 4: Query Records
            print("\n4. Querying Recorded Data from DB...")
            all_users = await user_repo.get_all()
            all_metrics = await metric_repo.get_all(employee_id=user.id)
            print(f"   [OK] Total Users in DB: {len(all_users)}")
            print(f"   [OK] Total Metrics for User: {len(all_metrics)}")

        print("\n==================================================")
        print(" SUCCESS: Database Connection & API Persistence Test PASSED!")
        print("==================================================")

    except Exception as e:
        print(f"\n[ERROR] Database Connection Failed: {e}\n")
        print("--- Full Error Traceback ---")
        traceback.print_exc()
        print("----------------------------\n")
        print("Troubleshooting Checklist:")
        print(" 1. Did you create a file named '.env' in 'd:\\CMProjects\\CognitiveMetricsAI_BE\\' ?")
        print(" 2. Inside .env, is DATABASE_URL set? E.g.:")
        print('    DATABASE_URL="postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require"')
        print(" 3. Check if password contains special characters (like @, #, %) that need URL-encoding.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
