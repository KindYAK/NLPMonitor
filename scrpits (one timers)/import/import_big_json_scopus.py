import datetime
import json

from mainapp.models import *


def chunks_iter(filename, chunksize=100):
    objects = []
    with open(filename, "r") as f:
        obj = ""
        for line in f:
            line = line.strip()
            obj += line
            if line == "}":
                objects.append(json.loads(obj))
                obj = ""
            if len(objects) >= chunksize:
                yield objects
                objects = []


corpus = Corpus.objects.create(name="scopus")
source = Source.objects.create(name="scopus", corpus=corpus)


for i, chunk in enumerate(chunks_iter("/scopuspubs.json", chunksize=10000)):
    print("!", i * 10000)
    docs = []
    for j, d in enumerate(chunk):
        try:
            year = int(d['year'])
            dt = datetime.datetime(year, 6, 1)
        except:
            dt = None
        docs.append(
            Document(
                source=source,
                title=f"{d['dc:title'][:450]} ({d['_id'][:20]}{i*10000+j})"[:499],
                text=d['dc:description'] + " " + d['authkeywords'],
                datetime=dt
            )
        )
    Document.objects.bulk_create(docs, ignore_conflicts=True)
