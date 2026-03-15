from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CreateCollectionSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
