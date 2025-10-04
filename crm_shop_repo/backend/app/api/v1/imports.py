from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.client import Client
from app.models.loyalty import LoyaltyCard
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.utils import norm_email, norm_phone, pick_identity
import pandas as pd
from io import BytesIO, StringIO
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _read_any(file: UploadFile) -> pd.DataFrame:
    content = file.file.read()
    name = file.filename.lower()
    try:
        if name.endswith(".xlsx") or name.endswith(".xls"):
            return pd.read_excel(BytesIO(content), dtype=str)
        else:
            # guess delimiter
            sample = content[:4096].decode("utf-8", errors="ignore")
            sep = max([",",";","\t","|"], key=lambda d: sample.count(d))
            return pd.read_csv(StringIO(content.decode("utf-8", errors="ignore")), sep=sep, dtype=str)
    except Exception:
        return pd.DataFrame()

def _resolve_client(db: Session, phone: str | None, client_ext: str | None, email: str | None) -> Client:
    # Priority: phone -> client_external_id -> email
    if phone:
        found = db.query(Client).filter(Client.phone==phone).first()
        if found: return found
    if client_ext:
        found = db.query(Client).filter(Client.client_external_id==client_ext).first()
        if found: return found
    if email:
        found = db.query(Client).filter(Client.email==email).first()
        if found: return found
    c = Client(phone=phone, client_external_id=client_ext, email=email, created_at=datetime.utcnow())
    db.add(c)
    db.flush()
    return c

@router.post("/clients")
def import_clients(file: UploadFile = File(...), db: Session = next(get_db())):
    df = _read_any(file)
    if df.empty:
        raise HTTPException(400, "Файл пуст или не распознан")

    # heuristic columns
    col = {c.lower(): c for c in df.columns}
    def pick(*keys):
        for k in keys:
            for name_lower, name in col.items():
                if k in name_lower: return name
        return None

    phone_c = pick("phone","тел","mobile","телефон","контакт")
    email_c = pick("email","почта","mail")
    id_c = pick("client_id","customer_id","id","код","uid")
    first_c = pick("first","имя")
    last_c = pick("last","фамил")
    middle_c = pick("second","отчество")
    city_c = pick("city","город")

    created, updated = 0, 0
    for _, r in df.iterrows():
        phone = norm_phone(str(r.get(phone_c))) if phone_c else None
        email = norm_email(str(r.get(email_c))) if email_c else None
        client_ext = str(r.get(id_c)).strip() if id_c and r.get(id_c) else None
        client = _resolve_client(db, phone, client_ext, email)
        # enrich
        if first_c and r.get(first_c): client.first_name = r.get(first_c)
        if last_c and r.get(last_c): client.last_name = r.get(last_c)
        if middle_c and r.get(middle_c): client.middle_name = r.get(middle_c)
        if city_c and r.get(city_c): client.city = r.get(city_c)
        updated += 1
    db.commit()
    return {"ok": True, "updated": updated, "total": len(df)}

@router.post("/loyalty")
def import_loyalty(file: UploadFile = File(...), db: Session = next(get_db())):
    df = _read_any(file)
    if df.empty:
        raise HTTPException(400, "Файл пуст или не распознан")

    col = {c.lower(): c for c in df.columns}
    def pick(*keys):
        for k in keys:
            for name_lower, name in col.items():
                if k in name_lower: return name
        return None

    phone_c = pick("phone","тел","mobile")
    email_c = pick("email","почта")
    id_c = pick("client_id","customer_id","id клиента")
    card_c = pick("card","карта","loyalty")
    tier_c = pick("tier","уровень","grade","статус")
    points_c = pick("points","bonus","баллы")
    balance_c = pick("balance","остаток")
    issued_c = pick("issued","выдан")
    expires_c = pick("expires","истекает")

    cnt = 0
    for _, r in df.iterrows():
        phone = norm_phone(str(r.get(phone_c))) if phone_c else None
        email = norm_email(str(r.get(email_c))) if email_c else None
        client_ext = str(r.get(id_c)).strip() if id_c and r.get(id_c) else None
        client = _resolve_client(db, phone, client_ext, email)

        card_id = str(r.get(card_c)).strip() if card_c and r.get(card_c) else None
        tier = str(r.get(tier_c)).strip() if tier_c and r.get(tier_c) else None
        points = str(r.get(points_c)).replace(",", ".") if points_c and r.get(points_c) else None
        balance = str(r.get(balance_c)).replace(",", ".") if balance_c and r.get(balance_c) else None
        issued_at = None
        expires_at = None

        lc = LoyaltyCard(card_id=card_id, client_id=client.id, tier=tier, points=points, balance=balance,
                         issued_at=issued_at, expires_at=expires_at, status=None)
        db.add(lc)
        cnt += 1
    db.commit()
    return {"ok": True, "imported": cnt}

@router.post("/purchases")
def import_purchases(file: UploadFile = File(...), db: Session = next(get_db())):
    df = _read_any(file)
    if df.empty:
        raise HTTPException(400, "Файл пуст или не распознан")

    col = {c.lower(): c for c in df.columns}
    def pick(*keys):
        for k in keys:
            for name_lower, name in col.items():
                if k in name_lower: return name
        return None

    order_c = pick("order","заказ","ordernumber","номер")
    date_c = pick("date","дата","создан")
    phone_c = pick("phone","тел","mobile")
    email_c = pick("email","почта")
    client_c = pick("client_id","customer_id","id клиента")
    sku_c = pick("sku","артикул","код")
    title_c = pick("title","товар","наименование")
    qty_c = pick("qty","кол-во","количество")
    price_c = pick("price","цена","стоимость")
    total_c = pick("total","итого","сумма")

    from decimal import Decimal, InvalidOperation

    def to_decimal(x):
        if x is None: return None
        s = str(x).replace(" ", "").replace(",", ".")
        try:
            return Decimal(s)
        except InvalidOperation:
            return None

    orders_seen = set()
    items = []
    imported_orders = 0

    for _, r in df.iterrows():
        order_id = str(r.get(order_c)).strip() if order_c and r.get(order_c) else None
        if not order_id:
            # skip junk rows
            continue
        phone = norm_phone(str(r.get(phone_c))) if phone_c else None
        email = norm_email(str(r.get(email_c))) if email_c else None
        client_ext = str(r.get(client_c)).strip() if client_c and r.get(client_c) else None
        client = _resolve_client(db, phone, client_ext, email)

        # save/merge purchase
        if order_id not in orders_seen:
            order_date_raw = r.get(date_c)
            order_dt = None
            if order_date_raw:
                for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S"):
                    try:
                        order_dt = datetime.strptime(str(order_date_raw), fmt)
                        break
                    except Exception:
                        continue

            total = to_decimal(r.get(total_c)) if total_c else None
            purchase = db.query(Purchase).get(order_id)
            if not purchase:
                purchase = Purchase(order_id=order_id, client_id=client.id, phone=phone, email=email,
                                    order_date=order_dt, total_amount=total, currency=None)
                db.add(purchase)
                imported_orders += 1
            else:
                # update if empty
                if not purchase.client_id: purchase.client_id = client.id
                if not purchase.phone and phone: purchase.phone = phone
                if not purchase.email and email: purchase.email = email
                if not purchase.order_date and order_dt: purchase.order_date = order_dt
                if not purchase.total_amount and total: purchase.total_amount = total

            orders_seen.add(order_id)

        # item line
        sku = str(r.get(sku_c)).strip() if sku_c and r.get(sku_c) else None
        title = str(r.get(title_c)).strip() if title_c and r.get(title_c) else None
        qty = to_decimal(r.get(qty_c)) if qty_c else None
        price = to_decimal(r.get(price_c)) if price_c else None
        if sku or title or qty or price:
            items.append(PurchaseItem(order_id=order_id, sku=sku, title=title, qty=qty, price=price))

    for it in items:
        db.add(it)
    db.commit()
    return {"ok": True, "orders_imported": imported_orders, "items_imported": len(items)}
