from fastapi import APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.client import Client
from app.models.purchase import Purchase
from sqlalchemy import func, and_
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("")
def create_segment(filters: dict = Body(...), db: Session = next(get_db())):
    # filters example: {"days_since_last_purchase_gt": 30, "has_phone": true, "city": "Москва"}
    query = db.query(Client)
    if filters.get("has_phone", None) is True:
        query = query.filter(Client.phone.isnot(None))
    if filters.get("has_email", None) is True:
        query = query.filter(Client.email.isnot(None))
    if "city" in filters:
        query = query.filter(Client.city == filters["city"])
    # days since last purchase
    if "days_since_last_purchase_gt" in filters:
        days = int(filters["days_since_last_purchase_gt"])
        subq = db.query(Purchase.client_id, func.max(Purchase.order_date).label("last_dt")).group_by(Purchase.client_id).subquery()
        query = query.join(subq, subq.c.client_id == Client.id, isouter=True)
        from datetime import datetime, timedelta
        dt = datetime.utcnow() - timedelta(days=days)
        query = query.filter((subq.c.last_dt.is_(None)) | (subq.c.last_dt < dt))

    rows = query.limit(100000).all()
    ids = [r.id for r in rows]
    return {"ok": True, "count": len(ids), "client_ids": ids}
