import json

from models.edition import Edition
from models.work import Work

if __name__ == "__main__":
    edition_isbn = "9780440062585"
    edition_data = Edition.get_from_isbn(edition_isbn)
    work_id_from_edition = edition_data.goodreads_work_id
    work_info = Work.get_work_data_by_goodreads_work_id(work_id_from_edition)
    editions = Edition.bulk_fetch_editions(work_info.goodreads_edition_ids)
    print(
        json.dumps({"work": work_info.dict(), "editions": [e.dict() for e in editions]})
    )
