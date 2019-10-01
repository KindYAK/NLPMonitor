from mainapp.models import Document
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from mainapp.services import batch_qs


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.preprocessing_raw_data()

    def preprocessing_raw_data(self):
        batch_size = 10000

        qs = Document.objects.filter(id__gt=0)

        for batch in batch_qs(qs, batch_size=batch_size):
            for doc in batch:
                doc.text = BeautifulSoup(doc.text, "html.parser").text.strip().replace('\n', '')
                doc.title = BeautifulSoup(doc.title, "html.parser").text.strip().replace('\n', '')
                Document.objects.bulk_update(batch, fields=['text', 'title'])
