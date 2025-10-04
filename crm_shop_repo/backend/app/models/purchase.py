from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric, DateTime, ForeignKey
from app.db.session import Base

class Purchase(Base):
    __tablename__ = "purchases"
    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clients.id", ondelete="SET NULL"))
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    order_date: Mapped[str | None] = mapped_column(DateTime)
    total_amount: Mapped[float | None] = mapped_column(Numeric(18,2))
    currency: Mapped[str | None] = mapped_column(String(8))
