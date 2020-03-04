import datetime
import json

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

from elasticsearch_dsl import Search

books = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("range", datetime={
                                                                            "gte": datetime.datetime(2019, 1, 1),
                                                                            "lte": datetime.datetime(2020, 1, 1),
                                                                        }
)[:500000].scan()

output = []
for book in books:
    output.append(
        {
            "_id": book.meta.id,
            "id": book.id,
            "source": book.source,
            "author": book.author if hasattr(book, "author") else None,
            "datetime": book.datetime,
            "title": book.title,
            "text": book.text,
            "url": book.url if hasattr(book, "url") else None,
            "num_views": book.num_views if hasattr(book, "num_views") else None,
        }
    )

with open("/output.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
