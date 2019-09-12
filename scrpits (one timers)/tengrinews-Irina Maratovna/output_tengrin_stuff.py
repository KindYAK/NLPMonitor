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
        "datetime": d.datetime.isoformat(),
        "number_of_img": d.html.count("<img"),
        "number_of_paragraphs": d.html.count("<p")
    })

with open("/output-IM.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
