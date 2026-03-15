from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import PasteVisibility


class Paste(TimestampMixin, db.Model):
    __tablename__ = "pastes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(16), nullable=False, unique=True, index=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    collection_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("collections.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_file: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    visibility: Mapped[PasteVisibility] = mapped_column(
        Enum(PasteVisibility, native_enum=False), nullable=False, default=PasteVisibility.UNLISTED
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    burn_after_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    owner = relationship("User", back_populates="pastes")
    collection = relationship("Collection", back_populates="pastes")
    tags = relationship(
        "PasteTag",
        back_populates="paste",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    reports = relationship("Report", back_populates="paste", lazy="selectin")

    __table_args__ = (
        Index("ix_pastes_owner_visibility", "owner_id", "visibility"),
    )


class PasteTag(db.Model):
    __tablename__ = "paste_tags"

    paste_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("pastes.id", ondelete="CASCADE"), primary_key=True
    )
    tag: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)

    paste = relationship("Paste", back_populates="tags")
