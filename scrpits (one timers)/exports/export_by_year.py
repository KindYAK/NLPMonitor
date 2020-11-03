import datetime
import json

from nlpmonitor.settings import ES_CLIENT, ES_INDEX_DOCUMENT

from elasticsearch_dsl import Search

books = Search(using=ES_CLIENT, index=ES_INDEX_DOCUMENT).filter("term", corpus="main").scan()

def is_kazakh(text, threshold=0.05):
    if text:
        kazakh_ratio = sum([c in "ӘәҒғҚқҢңӨөҰұҮүІі" for c in text]) / len(text)
        return kazakh_ratio > threshold
    else:
        return False

output = []
seen_ids = set()
for book in books:
    if is_kazakh(book.text + " " + book.title):
        continue
    if book.id in seen_ids:
        continue
    if len(output) % 100 == 0:
        print(len(output))
    output.append(
        {
            "_id": book.meta.id,
            "id": book.id,
            "source": book.source,
            "author": book.author if hasattr(book, "author") else None,
            "datetime": book.datetime if hasattr(book, "datetime") else None,
            "title": book.title,
            "text": book.text,
            "url": book.url if hasattr(book, "url") else None,
            "num_views": book.num_views if hasattr(book, "num_views") else None,
            "num_comments": book.num_comments if hasattr(book, "num_comments") else None,
            "num_likes": book.num_likes if hasattr(book, "num_likes") else None,
            "num_shares": book.num_shares if hasattr(book, "num_shares") else None,
        }
    )
    seen_ids.add(book.id)



with open("/output_ru.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
