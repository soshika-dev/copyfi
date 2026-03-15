from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class UpdateReportStatusSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    status: Literal["open", "reviewed", "actioned"]


class BanUserSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    is_banned: bool = True
