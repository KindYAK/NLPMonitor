from mainapp.models import Document

ds = Document.objects.filter(source__id=9)

for d in ds:
    if "/conference/" in d.url:
        d.type = 1
        d.save()
    if "/article/" in d.url:
        d.type = 2
        d.save()
    if "/opinion/" in d.url:
        d.type = 3
        d.save()
