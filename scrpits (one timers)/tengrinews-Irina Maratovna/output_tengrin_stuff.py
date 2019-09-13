import json

from mainapp.models import Document

ds = Document.objects.filter(source__id=9, type=0)

output = []
for d in ds:
    output.append({
        "title": d.title,
        "text": d.text,
        "type": dict(Document.TYPES)[d.type],
        "url": d.url,
        "datetime": d.datetime.isoformat() if d.datetime else "NaN",
        "number_of_img": d.html.count("<img") if d.html else "Nan",
        "number_of_paragraphs": d.html.count("<p") if d.html else "Nan"
    })

with open("/output-IM.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(output))
