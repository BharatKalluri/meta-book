import re
from functools import lru_cache
from typing import Optional

import requests
from requests import Response

FIRST_NUMBER_IN_URL_REGEX = r"/(\d+)"


@lru_cache(maxsize=50000)
def get_html_from_url(url: str) -> str:
    response: Response = requests.get(url)
    response_html = response.text
    return response_html


def get_goodreads_id_from_url(url: str) -> int:
    return int(re.search(r"/(\d+)", url).group(1))


def get_entity_id_from_canonical_url(soup) -> int:
    canonical_url: Optional[str] = soup.find("link", {"rel": "canonical"}).attrs.get(
        "href"
    )
    if not canonical_url:
        raise Exception("could not find canonical URL")
    return get_goodreads_id_from_url(canonical_url)
