import datetime
from typing import Optional

from pydantic import BaseModel

from models.externalLink import ExternalLink


class Author(BaseModel):
    goodreads_id: int
    name: str
    bio: str
    links: list[ExternalLink] = []
    born_place: Optional[str]
    born_time: Optional[datetime.date]
    twitter_handle: Optional[str]
    genres: Optional[list[str]]
    website: Optional[str]
