# Connecting Neon PostgreSQL Database to CognitiveMetricsAI_BE

This guide explains how to connect your **Neon Serverless PostgreSQL** database to `CognitiveMetricsAI_BE` and run the end-to-end test script to verify table initialization and API data persistence.

---

## Step-by-Step Setup Guide

### 1. Retrieve your Neon Connection String

1. Log into your [Neon Console](https://console.neon.tech).
2. Select your project and navigate to **Dashboard** or **Connection Details**.
3. Copy the PostgreSQL connection string. It will look like:
   ```text
   postgresql://alex_owner:npg_xYz12345@ep-cool-flower-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

---

### 2. Configure `.env` in `CognitiveMetricsAI_BE`

1. Inside `d:\CMProjects\CognitiveMetricsAI_BE`, create a `.env` file (or copy `.env.example` to `.env`).
2. Add your Neon connection string to `DATABASE_URL`:
   ```env
   PROJECT_NAME="Cognitive Metrics AI Backend"
   API_V1_STR="/api/v1"
   CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]

   # Paste your Neon PostgreSQL connection string here:
   DATABASE_URL="postgresql://alex_owner:npg_xYz12345@ep-cool-flower-123456.us-east-2.aws.neon.tech/neondb?sslmode=require"
   ```

> **Note**: The backend automatically converts `postgresql://` to `postgresql+asyncpg://` so `asyncpg` connects seamlessly with SSL to Neon.

---

### 3. Run the Database Connection & Verification Script

Run the automated test script from `CognitiveMetricsAI_BE`:

```bash
python scripts/test_db_connection.py
```

#### What the test script verifies:
1. **Schema Initialization**: Auto-creates `users`, `metrics`, `performance_reviews`, and `goals` tables in your Neon PostgreSQL database.
2. **Enterprise Custom Metadata**: Inserts a sample user with nested JSON `custom_metadata`.
3. **Metric Logging**: Inserts cognitive metric records linked to the user.
4. **Data Querying**: Queries the Neon database to confirm reading/writing works perfectly.

---

### 4. Start the FastAPI Server with Neon

Once the test script passes, start your live server:

```bash
uvicorn app.main:app --reload --port 8000
```

Open interactive Swagger docs at [http://localhost:8000/docs](http://localhost:8000/docs) to test API endpoints against your live Neon database!
