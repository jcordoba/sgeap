# SGEAP Backend

Sistema de Gestión de Expedientes Académicos para Programas - API

## Stack
- FastAPI + Python 3.11+
- SQLAlchemy 2.0
- Alembic (migrations)
- PostgreSQL 15+
- JWT Auth (básico)

## Estructura
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py           # DB connection
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── routers/              # API endpoints
│   ├── services/             # Business logic
│   └── utils/                # Helpers
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
├── .env.example
├── requirements.txt
└── alembic.ini
```

## Run
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## API Base
http://localhost:8000/api