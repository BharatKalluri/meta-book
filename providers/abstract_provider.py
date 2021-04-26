from abc import ABC

from constants import ProviderList
from models.author import Author
from models.edition import Edition
from models.work import Work


class AbstractProvider(ABC):
    @staticmethod
    def get_work_data_from_provider_work_id(provider_work_id: int) -> Work:
        pass

    @staticmethod
    def get_edition_data_from_isbn(isbn: str) -> Edition:
        pass

    @staticmethod
    def get_edition_from_provider_edition_id(goodreads_edition_id: int) -> Edition:
        pass

    @staticmethod
    def bulk_fetch_editions(provider_edition_id_list: list[int]) -> list[Edition]:
        pass

    @staticmethod
    def get_provider_name() -> ProviderList:
        pass

    @staticmethod
    def get_author_from_provider_author_id(goodreads_author_id: int) -> Author:
        pass
