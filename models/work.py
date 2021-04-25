from __future__ import annotations

from typing import Optional

from bs4 import BeautifulSoup
from pydantic import BaseModel

from utils import (
    get_goodreads_id_from_url,
    get_entity_id_from_canonical_url,
    get_html_from_url,
)


class WorkAuthorInfo(BaseModel):
    name: str
    author_id: int


class Work(BaseModel):
    goodreads_id: int
    title: str
    authors: list[WorkAuthorInfo]
    goodreads_edition_ids: list[int]

    @staticmethod
    def get_work_data_from_work_page(raw_html) -> Work:
        # TODO: need to follow pagination here
        soup = BeautifulSoup(raw_html, "html.parser")

        goodreads_work_id: str = get_entity_id_from_canonical_url(soup)

        author_el_arr = soup.find("h2").find_all("a")
        author_info_arr = [
            WorkAuthorInfo(
                name=el.text, author_id=get_goodreads_id_from_url(el.attrs.get("href"))
            )
            for el in author_el_arr
        ]

        title: str = soup.find("h1").text.replace("> Editions", "").strip()
        edition_url_els = soup.find_all("a", {"class": "bookTitle"})
        complete_edition_urls: list[Optional[str]] = [
            el.attrs.get("href") for el in edition_url_els
        ]
        edition_ids: list[int] = [
            get_goodreads_id_from_url(el) for el in complete_edition_urls
        ]
        return Work(
            goodreads_id=goodreads_work_id,
            title=title,
            authors=author_info_arr,
            goodreads_edition_ids=edition_ids,
        )

    @staticmethod
    def get_work_data_by_goodreads_work_id(goodreads_work_id: str) -> Work:
        response_html = get_html_from_url(
            f"https://www.goodreads.com/work/editions/{goodreads_work_id}?utf8=%E2%9C%93&per_page=100"
        )
        return Work.get_work_data_from_work_page(response_html)
