from __future__ import annotations

import re
from typing import Optional, Match

from bs4 import BeautifulSoup
from pydantic import BaseModel

from utils import (
    get_html_from_url,
    get_goodreads_id_from_url,
    get_entity_id_from_canonical_url,
)


class EditionAuthorInfo(BaseModel):
    name: str
    comment: Optional[str]
    author_id: int


class Edition(BaseModel):
    goodreads_id: int
    goodreads_work_id: int
    title: str
    description: Optional[str]
    goodreads_authors_info: list[EditionAuthorInfo]
    book_format: Optional[str]
    languages: Optional[list[str]]
    isbn_10: Optional[str]
    isbn_13: Optional[str]
    asin: Optional[str]

    # TODO: add page_count, publisher, published_on

    @staticmethod
    def get_edition_data_from_edition_page(raw_html: str) -> Edition:
        soup = BeautifulSoup(raw_html, "html.parser")

        goodreads_edition_id: int = get_entity_id_from_canonical_url(soup)

        other_edition_actions_el: list = soup.findAll(
            "div", {"class": "otherEditionsActions"}
        )
        all_editions_link: Optional[str] = (
            other_edition_actions_el[0].find("a", text="All Editions").attrs.get("href")
            if len(other_edition_actions_el) > 0
            else None
        )
        goodreads_work_id: int = get_goodreads_id_from_url(all_editions_link)

        edition_title: str = soup.find(id="bookTitle").text.strip()

        edition_description_list: list = list(
            soup.find(id="description").findAll("span")
        )
        edition_description: str = (
            edition_description_list[1].text
            if len(edition_description_list) > 1
            else edition_description_list[0].text
        )

        author_container_elements = soup.findAll(
            "div", {"class": "authorName__container"}
        )

        authors_info_dicts: list[dict[str, str]] = [
            {
                "name": el.find("a").text,
                "author_link": el.find("a").attrs.get("href"),
                "comment": el.find("span", {"class": "greyText"}).text
                if el.find("span", {"class": "greyText"})
                else None,
            }
            for el in author_container_elements
        ]

        author_infos: list[EditionAuthorInfo] = [
            EditionAuthorInfo(
                name=el.get("name"),
                comment=el.get("comment"),
                author_id=get_goodreads_id_from_url(el.get("author_link")),
            )
            for el in authors_info_dicts
        ]

        book_format_span = soup.find("span", {"itemprop": "bookFormat"})
        book_format: str = book_format_span.text if book_format_span else None
        languages_el = soup.find("div", {"itemProp": "inLanguage"})
        languages: Optional[list[str]] = (
            languages_el.text.split(",") if languages_el else None
        )

        row_title_arr = soup.find_all("div", {"class": "infoBoxRowTitle"})
        row_item_arr = soup.find_all("div", {"class": "infoBoxRowItem"})
        title_item_map: list[dict[str, str]] = [
            {"title": title.text, "item": item.text}
            for title, item in zip(row_title_arr, row_item_arr)
        ]
        filter_for_isbn: list[dict[str, str]] = list(
            filter(lambda el: el["title"].lower() == "isbn", title_item_map)
        )
        isbn_raw_str: Optional[str] = (
            filter_for_isbn[0]["item"] if len(filter_for_isbn) > 0 else None
        )
        isbn_matches: Optional[Match[str]] = (
            re.search(r"(\d{10})\D+13: (\d{13})", isbn_raw_str)
            if isbn_raw_str
            else None
        )
        isbn_10, isbn_13 = (
            (isbn_matches.group(1), isbn_matches.group(2))
            if isbn_matches
            else (None, None)
        )

        asin_search: Optional[Match[str]] = re.search(r"asin: (\S{10})", raw_html)
        asin: Optional[str] = asin_search.group(1) if asin_search else None

        return Edition(
            goodreads_id=goodreads_edition_id,
            goodreads_work_id=goodreads_work_id,
            title=edition_title,
            description=edition_description,
            goodreads_authors_info=author_infos,
            book_format=book_format,
            languages=languages,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            asin=asin,
        )

    @staticmethod
    def get_from_isbn(isbn: str) -> Edition:
        response_html = get_html_from_url(f"https://www.goodreads.com/search?q={isbn}")
        return Edition.get_edition_data_from_edition_page(response_html)

    @staticmethod
    def get_from_goodreads_edition_id(goodreads_edition_id: int):
        print(f"fetching for {goodreads_edition_id}")
        response_html = get_html_from_url(
            f"https://www.goodreads.com/book/show/{goodreads_edition_id}"
        )
        return Edition.get_edition_data_from_edition_page(response_html)

    @staticmethod
    def bulk_fetch_editions(edition_id_list: list[int]):
        return [
            Edition.get_from_goodreads_edition_id(edition_id)
            for edition_id in edition_id_list
        ]
