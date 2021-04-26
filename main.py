import json

from constants import ProviderList
from providers.abstract_provider import AbstractProvider
from providers.provider_utils import get_provider_class

if __name__ == "__main__":

    provider: AbstractProvider = get_provider_class(ProviderList.GOODREADS)

    edition_isbn = "9780440062585"
    edition_data = provider.get_edition_data_from_isbn(edition_isbn)
    work_id_from_edition = edition_data.provider_work_id
    work_info = provider.get_work_data_from_provider_work_id(work_id_from_edition)
    editions = provider.bulk_fetch_editions(work_info.provider_edition_ids)
    print(
        json.dumps({"work": work_info.dict(), "editions": [e.dict() for e in editions]})
    )
