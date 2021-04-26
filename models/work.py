from __future__ import annotations

from pydantic import BaseModel


class WorkAuthorInfo(BaseModel):
    name: str
    provider_author_id: int


class Work(BaseModel):
    provider_id: int
    title: str
    authors: list[WorkAuthorInfo]
    provider_edition_ids: list[int]
