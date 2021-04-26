from __future__ import annotations

import re
from re import Match
from typing import Optional

from bs4 import BeautifulSoup

from constants import ProviderList
from models.author import Author
from models.edition import Edition, EditionAuthorInfo
from models.work import WorkAuthorInfo, Work
from providers.abstract_provider import AbstractProvider
from utils import (
    get_html_from_url,
)

FIRST_NUMBER_IN_URL_REGEX = r"/(\d+)"


class GoodreadsScraper(AbstractProvider):
    @staticmethod
    def _get_goodreads_id_from_url(url: str) -> int:
        return int(re.search(FIRST_NUMBER_IN_URL_REGEX, url).group(1))

    @staticmethod
    def get_provider_name() -> ProviderList:
        return ProviderList.GOODREADS

    @staticmethod
    def _get_entity_id_from_canonical_url(soup) -> int:
        canonical_url: Optional[str] = soup.find(
            "link", {"rel": "canonical"}
        ).attrs.get("href")
        if not canonical_url:
            raise Exception("could not find canonical URL")
        return GoodreadsScraper._get_goodreads_id_from_url(canonical_url)

    @staticmethod
    def _get_table_contents_map(
        soup, row_title_class_name: str, row_item_class_name: str
    ) -> list[dict[str, str]]:
        row_title_arr = soup.find_all("div", {"class": row_title_class_name})
        row_item_arr = soup.find_all("div", {"class": row_item_class_name})
        title_item_map: list[dict[str, str]] = [
            {"title": title.text, "item": item.text}
            for title, item in zip(row_title_arr, row_item_arr)
        ]
        return title_item_map

    @staticmethod
    def _get_edition_data_from_html(raw_html: str) -> Edition:
        soup = BeautifulSoup(raw_html, "html.parser")

        goodreads_edition_id: int = GoodreadsScraper._get_entity_id_from_canonical_url(
            soup
        )

        other_edition_actions_el: list = soup.findAll(
            "div", {"class": "otherEditionsActions"}
        )
        all_editions_link: Optional[str] = (
            other_edition_actions_el[0].find("a", text="All Editions").attrs.get("href")
            if len(other_edition_actions_el) > 0
            else None
        )
        goodreads_work_id: int = GoodreadsScraper._get_goodreads_id_from_url(
            all_editions_link
        )

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
                author_id=GoodreadsScraper._get_goodreads_id_from_url(
                    el.get("author_link")
                ),
            )
            for el in authors_info_dicts
        ]

        book_format_span = soup.find("span", {"itemprop": "bookFormat"})
        book_format: str = book_format_span.text if book_format_span else None
        languages_el = soup.find("div", {"itemProp": "inLanguage"})
        languages: Optional[list[str]] = (
            languages_el.text.split(",") if languages_el else None
        )

        title_item_map: list[dict[str, str]] = GoodreadsScraper._get_table_contents_map(
            soup, "infoBoxRowTitle", "infoBoxRowItem"
        )
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

        cover_url_el = soup.find("img", {"id": "coverImage"})
        cover_url: Optional[str] = (
            cover_url_el.attrs.get("src") if cover_url_el else None
        )

        return Edition(
            provider_id=goodreads_edition_id,
            provider_work_id=goodreads_work_id,
            title=edition_title,
            description=edition_description,
            editor_authors_info=author_infos,
            book_format=book_format,
            languages=languages,
            isbn_10=isbn_10,
            isbn_13=isbn_13,
            asin=asin,
            cover_url=cover_url,
        )

    @staticmethod
    def _get_author_data_from_html(raw_html: str):
        soup = BeautifulSoup(raw_html, "html.parser")
        goodreads_author_id = GoodreadsScraper._get_entity_id_from_canonical_url(soup)

        author_name_el = soup.find("h1", {"class": "authorName"})
        author_name = author_name_el.text.strip() if author_name_el else None
        if not author_name:
            raise Exception(f"No author name found for {goodreads_author_id}")

        author_bio_el = soup.find("div", {"class": "aboutAuthorInfo"})
        author_bio = (
            author_bio_el.text.replace("edit data", "").replace("..more", "").strip()
            if author_name_el
            else None
        )

        title_item_map = GoodreadsScraper._get_table_contents_map(
            soup, "dataTitle", "dataItem"
        )
        filtered_author_website_list = list(
            filter(lambda el: el.get("title") == "Website", title_item_map)
        )
        author_website_raw = (
            filtered_author_website_list[0].get("item")
            if len(filtered_author_website_list) > 0
            else None
        )
        author_website = author_website_raw.strip() if author_website_raw else None
        # TODO: add twitter handle, born_place and born_time
        return Author(
            provider_id=goodreads_author_id,
            name=author_name,
            bio=author_bio,
            website=author_website,
        )

    @staticmethod
    def _get_work_data_from_raw_html(raw_html) -> Work:
        # TODO: need to follow pagination here
        soup = BeautifulSoup(raw_html, "html.parser")

        goodreads_work_id: int = GoodreadsScraper._get_entity_id_from_canonical_url(
            soup
        )

        author_el_arr = soup.find("h2").find_all("a")
        author_info_arr = [
            WorkAuthorInfo(
                name=el.text,
                provider_author_id=GoodreadsScraper._get_goodreads_id_from_url(
                    el.attrs.get("href")
                ),
            )
            for el in author_el_arr
        ]

        title: str = soup.find("h1").text.replace("> Editions", "").strip()
        edition_url_els = soup.find_all("a", {"class": "bookTitle"})
        complete_edition_urls: list[Optional[str]] = [
            el.attrs.get("href") for el in edition_url_els
        ]
        edition_ids: list[int] = [
            GoodreadsScraper._get_goodreads_id_from_url(el)
            for el in complete_edition_urls
        ]
        return Work(
            provider_id=goodreads_work_id,
            title=title,
            authors=author_info_arr,
            provider_edition_ids=edition_ids,
        )

    @staticmethod
    def get_work_data_from_provider_work_id(provider_work_id: int) -> Work:
        response_html = get_html_from_url(
            f"https://www.goodreads.com/work/editions/{provider_work_id}?utf8=%E2%9C%93&per_page=100"
        )
        return GoodreadsScraper._get_work_data_from_raw_html(response_html)

    @staticmethod
    def get_edition_data_from_isbn(isbn: str) -> Edition:
        response_html = get_html_from_url(f"https://www.goodreads.com/search?q={isbn}")
        return GoodreadsScraper._get_edition_data_from_html(response_html)

    @staticmethod
    def get_author_from_provider_author_id(goodreads_author_id: int) -> Author:
        print(f"author info: {goodreads_author_id}")
        response_html = get_html_from_url(
            f"https://www.goodreads.com/author/show/{goodreads_author_id}"
        )
        return GoodreadsScraper._get_author_data_from_html(response_html)

    @staticmethod
    def get_edition_from_provider_edition_id(goodreads_edition_id: int) -> Edition:
        print(f"fetching for {goodreads_edition_id}")
        response_html = get_html_from_url(
            f"https://www.goodreads.com/book/show/{goodreads_edition_id}"
        )
        return GoodreadsScraper._get_edition_data_from_html(response_html)

    @staticmethod
    def bulk_fetch_editions(provider_edition_id_list: list[int]) -> list[Edition]:
        return [
            GoodreadsScraper.get_edition_from_provider_edition_id(provider_edition_id)
            for provider_edition_id in provider_edition_id_list
        ]
