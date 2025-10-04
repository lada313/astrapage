from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Date, Boolean, DateTime
from app.db.session import Base

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    client_external_id: Mapped[str | None] = mapped_column(String(128), index=True)
    first_name: Mapped[str | None] = mapped_column(String(128))
    last_name: Mapped[str | None] = mapped_column(String(128))
    middle_name: Mapped[str | None] = mapped_column(String(128))
    city: Mapped[str | None] = mapped_column(String(128))
    birth_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(16))
    consent_email: Mapped[bool | None] = mapped_column(Boolean)
    consent_sms: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[str | None] = mapped_column(DateTime)
