from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from app.db.session import Base

class Segment(Base):
    __tablename__ = "segments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    filters_json: Mapped[str | None] = mapped_column(Text)
    size: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[str | None] = mapped_column(DateTime)

class SegmentMember(Base):
    __tablename__ = "segment_members"
    segment_id: Mapped[int] = mapped_column(Integer, ForeignKey("segments.id", ondelete="CASCADE"), primary_key=True)
    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), primary_key=True)
