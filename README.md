# Cognitive Metrics AI Backend (FastAPI)

FastAPI backend service powering the `CognitiveMetricsAI_FE` Vue frontend application. Designed with an extensible Clean Architecture to allow enterprise clients to connect their own database schemas seamlessly.

## Key Features

- **Multi-Database Support**: SQLAlchemy 2.0 Async engine supporting PostgreSQL, MySQL, SQLite, and MS SQL Server.
- **Enterprise Schema Extensibility**: Dynamic `custom_metadata` JSON fields on core models + Abstract Repository Pattern.
- **Auto Database Initialization**: Automatically initializes tables on startup for quick local development.
- **Interactive Documentation**: Built-in Swagger UI and ReDoc interfaces.

## Documentation

For a comprehensive guide explaining all API endpoints, request/response payloads, and enterprise schema integration models, see:
👉 [API Documentation & Integration Guide](docs/API_DOCUMENTATION.md)

## Requirements

- Python 3.10+

## Quick Start

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux/macOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Configuration (Optional):**
   By default, the server uses a local `sqlite+aiosqlite:///./cognitive_metrics.db` file. To connect to PostgreSQL or another database, create a `.env` file:
   ```env
   DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/cognitive_metrics_db"
   ```

4. **Start the FastAPI development server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Access Interactive API Docs:**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
