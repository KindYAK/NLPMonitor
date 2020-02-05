import datetime

from mainapp.models import *
from mainapp.services import batch_qs

batch_size = 10000

qs = Document.objects.filter(id__gt=0).order_by('id')
number_of_documents = qs.count()
for i, batch in enumerate(batch_qs(qs, batch_size=batch_size)):
    print(f"Processing {i*batch_size}/{number_of_documents}")
    for j, doc in enumerate(batch):
        if i == 0:
            print(f"{j}/{batch_size}")
        print("!", doc.datetime)
        if doc.datetime and doc.datetime.date() > datetime.datetime.now().date():
            actual_date = doc.datetime + datetime.timedelta(hours=6)
            if actual_date.day <= 12:
                doc.datetime = doc.datetime.replace(month=actual_date.day, day=actual_date.month)
    Document.objects.bulk_update(batch, fields=['datetime'])
