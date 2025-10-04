# CRM Shop (Self-Hosted, No Paid Services)

- Stack: FastAPI + PostgreSQL + SQLAlchemy + Alembic, React + Vite.
- Import CSV: clients, loyalty cards, purchases (orders & items). 
- Matching priority for identity resolution: **phone → client_id → email**.
- Segments export as CSV (ready for email/SMS services).
- No email sending for now (per your request).

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
# API docs: http://localhost:8000/docs
# Frontend: http://localhost:5173
```
