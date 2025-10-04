from fastapi import APIRouter, Body
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.client import Client
import csv, os
from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter()

STORAGE = Path("/app/storage/exports")
STORAGE.mkdir(parents=True, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/csv")
def export_csv(body: dict = Body(...), db: Session = next(get_db())):
    # body: {"client_ids": [1,2,3], "fields": ["phone","first_name","last_name"]}
    ids = body.get("client_ids") or []
    fields = body.get("fields") or ["phone","first_name","last_name"]
    q = db.query(Client).filter(Client.id.in_(ids)) if ids else db.query(Client)
    rows = q.all()
    out = STORAGE / "segment_export.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            w.writerow([getattr(r, c, "") or "" for c in fields])
    return FileResponse(out.as_posix(), filename="segment_export.csv")
