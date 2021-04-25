from pydantic import BaseModel


class ExternalLink(BaseModel):
    url: str
    description: str
