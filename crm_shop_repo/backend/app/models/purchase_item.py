from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Numeric, ForeignKey
from app.db.session import Base

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[str] = mapped_column(String(64), ForeignKey("purchases.order_id", ondelete="CASCADE"))
    sku: Mapped[str | None] = mapped_column(String(64))
    title: Mapped[str | None] = mapped_column(String(255))
    qty: Mapped[float | None] = mapped_column(Numeric(18,3))
    price: Mapped[float | None] = mapped_column(Numeric(18,2))
