# Meta Book
### Work in progress 🚧

A library & a command line utility to get data metadata
of books using different sources (providers)

### Providers

- Goodreads
- Google API (coming soon)

Feel free to recommend new providers!

### Usage

Currently, it's not packaged as a python package.

This is how the python API looks as of now

```python
edition_isbn = "162097066X"
provider: AbstractProvider = get_provider_class(ProviderList.GOODREADS)
edition_data: Edition = provider.get_edition_data_from_isbn(edition_isbn)
work_id_from_edition: int = edition_data.provider_work_id
work_info: Work = provider.get_work_data_from_provider_work_id(work_id_from_edition)
editions: list[Edition] = provider.bulk_fetch_editions(work_info.provider_edition_ids)
```

[Output of the above in json]()