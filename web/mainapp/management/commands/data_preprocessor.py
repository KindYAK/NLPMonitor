from mainapp.models import Document
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from mainapp.services import batch_qs


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.preprocessing_raw_data()

    def preprocessing_raw_data(self):
        batch_size = 10000

        def is_kazakh(text):
            return sum([c in "ӘәҒғҚқҢңӨөҰұҮүІі" for c in text]) > 0.04

        qs = Document.objects.filter(id__gt=0)
        number_of_documents = qs.count()
        for i, batch in enumerate(batch_qs(qs, batch_size=batch_size)):
            print(f"Processing {i*batch_size}/{number_of_documents}")
            for doc in batch:
                doc.text = BeautifulSoup(doc.text, "html.parser").text.strip().replace('\n', '')
                doc.title = BeautifulSoup(doc.title, "html.parser").text.strip().replace('\n', '')
            Document.objects.bulk_update(batch, fields=['text', 'title'])
        for i, batch in enumerate(batch_qs(qs, batch_size=batch_size)):
            print(f"Deleting {i*batch_size}/{number_of_documents}")
            for doc in batch:
                if is_kazakh(doc.text + doc.title):
                    doc.delete()
