from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class EditionAuthorInfo(BaseModel):
    name: str
    comment: Optional[str]
    author_id: int


class Edition(BaseModel):
    provider_id: int
    # TODO: provider work ID may not exist for providers like amazon, need to rethink
    provider_work_id: int
    title: str
    description: Optional[str]
    editor_authors_info: list[EditionAuthorInfo]
    book_format: Optional[str]
    languages: Optional[list[str]]
    isbn_10: Optional[str]
    isbn_13: Optional[str]
    asin: Optional[str]
    cover_url: Optional[str]
    # TODO: add page_count, publisher, published_on
