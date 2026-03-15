from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaginationSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


def parse_pagination(args: Mapping[str, Any]) -> PaginationSchema:
    return PaginationSchema.model_validate(
        {
            "page": args.get("page", 1),
            "limit": args.get("limit", 20),
        }
    )
