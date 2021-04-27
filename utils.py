from functools import lru_cache

import requests
from requests import Response


@lru_cache(maxsize=50000)
def get_html_from_url(url: str) -> str:
    # TODO: aggressively cache, maybe using redis?
    response: Response = requests.get(url)
    response_html = response.text
    return response_html
