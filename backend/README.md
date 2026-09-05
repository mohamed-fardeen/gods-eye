# Chennai Digital Twin - Backend Architecture (Phase 1)

**CURRENT STATE = ARCHITECTURE ONLY.**

This repository contains the foundational architecture for the Chennai Digital Twin backend. It is designed as a **Modular Monolith** to ensure clear separation of concerns (API, services, AI interfaces, database) while keeping deployment simple before microservices are genuinely needed.

## Phase 1 Capabilities
Currently, this backend operates purely as a structural skeleton:
- It configures the FastAPI application, database connections, and Alembic migrations.
- It defines the SQLAlchemy Object Relational Models mapping to PostGIS data types.
- **Strictly No Fake Data**: All intelligence and data retrieval API endpoints are currently stubbed. Hitting them returns `{"status": "not_implemented", "phase": "2"}` to ensure real logic is implemented later.
- No AI inference, video processing, or analytics logic is running.

## Future Architecture (Phase 2 & 3)
In the future, this backend will evolve to connect the frontend to real-world sensors, video feeds, and machine learning models:
- **AI Modules**: The `app/ai/` directory contains Protocol interfaces where future Python ML models (YOLO, DeepSORT, LPRNet) will be injected.
- **Service Layer**: The `app/services/` layer will handle the orchestration between database repositories and the AI inference engines.
- **Real-Time Integration**: The `app/api/v1/ws.py` WebSocket boundary will stream live incident updates and vehicle tracking telemetry to the command-center frontend.

## Folder Structure

```
backend/
├── alembic/              # Database migration scripts
├── app/
│   ├── api/v1/           # FastAPI router endpoints (REST + WebSocket)
│   ├── core/             # Application config and database connection setup
│   ├── models/           # SQLAlchemy ORM definitions (City, Vehicles, Cameras, etc.)
│   ├── schemas/          # Pydantic data validation contracts
│   ├── services/         # Business logic layer (Stubs)
│   ├── repositories/     # Database access abstraction (Stubs)
│   └── ai/               # AI interface boundaries (vehicle detection, OCR, etc.)
├── tests/                # Pytest unit testing
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Local PostgreSQL + PostGIS setup
└── README.md             # This file
```

## How Frontend Communicates with Backend
The existing React/Vite frontend will eventually communicate with this backend via:
1. **REST APIs** (`/api/v1/*`): To fetch static infrastructure, historical analytics, and configuration.
2. **WebSockets** (`/api/v1/ws/events`): For low-latency streaming of vehicle positions, camera alerts, and traffic updates onto the CesiumJS map.

## Setup & Running Locally

### 1. Environment Variables
Create a `.env` file in the `backend/` directory or rely on the defaults defined in `app/core/config.py`:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgrespassword
POSTGRES_DB=chennai_twin
POSTGRES_PORT=5432
```

### 2. Database Setup
Start the local PostgreSQL instance (with PostGIS extensions) via Docker:
```bash
cd backend
docker-compose up -d
```

### 3. Run FastAPI
Create a virtual environment, install dependencies, and start the development server:
```bash
# In the backend directory
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload
```

You can then visit `http://localhost:8000/docs` to view the interactive API documentation and explore the Phase 1 endpoint contracts.
