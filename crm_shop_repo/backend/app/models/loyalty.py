from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric, Date, ForeignKey
from app.db.session import Base

class LoyaltyCard(Base):
    __tablename__ = "loyalty_cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[str | None] = mapped_column(String(64), index=True)
    client_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clients.id", ondelete="SET NULL"))
    tier: Mapped[str | None] = mapped_column(String(64))
    points: Mapped[float | None] = mapped_column(Numeric(18,4))
    balance: Mapped[float | None] = mapped_column(Numeric(18,4))
    issued_at: Mapped[str | None] = mapped_column(Date)
    expires_at: Mapped[str | None] = mapped_column(Date)
    status: Mapped[str | None] = mapped_column(String(64))
