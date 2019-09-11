import json

from mainapp.models import Document

ds = Document.objects.filter(source__id=9, type__gte=1)

output = []
for d in ds:
    output.append({
        "title": d.title,
        "text": d.text,
        "type": dict(Document.TYPES)[d.type],
        "url": d.url,
        "datetime": d.datetime,
        "number_of_img": d.html.dount("<img"),
        "number_of_paragraphs": d.html.count("<p")
    })

with open("/backup/output-IM.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
