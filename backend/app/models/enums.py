from __future__ import annotations

import enum


class UserRole(enum.StrEnum):
    USER = "user"
    ADMIN = "admin"


class PasteVisibility(enum.StrEnum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class ReportStatus(enum.StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
