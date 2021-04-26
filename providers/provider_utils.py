from constants import ProviderList
from providers.goodreads_scraper import GoodreadsScraper


def get_provider_class(provider_id: ProviderList):
    # TODO: fix this, need to automatically collect subclasses of abstract provider
    subclasses_to_abstract_class: list[type] = [GoodreadsScraper]

    subclass_to_return_list = list(
        filter(
            lambda el: el.get_provider_name() == provider_id,
            subclasses_to_abstract_class,
        )
    )
    if len(subclass_to_return_list) == 1:
        return subclass_to_return_list[0]
    else:
        raise Exception(f"Cannot find provider for {provider_id}")
