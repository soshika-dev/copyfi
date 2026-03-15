from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


VisibilityLiteral = Literal["public", "unlisted", "private"]
ExpiryLiteral = Literal["10m", "1h", "1d", "1w", "1m", "never"]


class CreatePasteSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, max_length=200)
    content: str = Field(min_length=1, max_length=512 * 1024)
    language: str | None = Field(default=None, max_length=50)
    visibility: VisibilityLiteral = "unlisted"
    password: str | None = Field(default=None, min_length=1, max_length=128)
    expires_in: ExpiryLiteral = "never"
    burn_after_read: bool = False
    tags: list[str] = Field(default_factory=list, max_length=20)
    collection_id: uuid.UUID | None = None

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, tags: list[str]) -> list[str]:
        cleaned: list[str] = []
        for tag in tags:
            normalized = tag.strip().lower()
            if not normalized:
                continue
            if len(normalized) > 50:
                raise ValueError("tag length must be <= 50")
            cleaned.append(normalized)
        return sorted(set(cleaned))


class UpdatePasteSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=512 * 1024)
    language: str | None = Field(default=None, max_length=50)
    visibility: VisibilityLiteral | None = None
    password: str | None = Field(default=None, min_length=1, max_length=128)
    clear_password: bool = False
    expires_in: ExpiryLiteral | None = None
    burn_after_read: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=20)
    collection_id: uuid.UUID | None = None

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, tags: list[str] | None) -> list[str] | None:
        if tags is None:
            return None
        cleaned: list[str] = []
        for tag in tags:
            normalized = tag.strip().lower()
            if not normalized:
                continue
            if len(normalized) > 50:
                raise ValueError("tag length must be <= 50")
            cleaned.append(normalized)
        return sorted(set(cleaned))


class ReportSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    reason: str = Field(min_length=3, max_length=1000)
