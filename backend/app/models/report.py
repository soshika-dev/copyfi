from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ReportStatus


class Report(TimestampMixin, db.Model):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    paste_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("pastes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reporter_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    reporter_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus, native_enum=False), nullable=False, default=ReportStatus.OPEN, index=True
    )

    paste = relationship("Paste", back_populates="reports")
    reporter_user = relationship("User", back_populates="reports")
