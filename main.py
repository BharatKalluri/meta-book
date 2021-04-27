import json

from constants import ProviderList
from models.edition import Edition
from models.work import Work
from providers.abstract_provider import AbstractProvider
from providers.provider_utils import get_provider_class

if __name__ == "__main__":
    edition_isbn = "162097066X"
    provider: AbstractProvider = get_provider_class(ProviderList.GOODREADS)
    edition_data: Edition = provider.get_edition_data_from_isbn(edition_isbn)
    work_id_from_edition: int = edition_data.provider_work_id
    work_info: Work = provider.get_work_data_from_provider_work_id(work_id_from_edition)
    editions: list[Edition] = provider.bulk_fetch_editions(
        work_info.provider_edition_ids
    )
    print(
        json.dumps(
            {
                "work": work_info.dict(),
                "editions": [
                    {
                        "data": edition_data.dict(),
                        "authors_info": [
                            {
                                "data": provider.get_author_from_provider_author_id(
                                    el.author_id
                                ).dict(),
                                "comment": el.comment,
                            }
                            for el in edition_data.editor_authors_info
                        ],
                    }
                    for edition_data in editions
                ],
            }
        )
    )
