from django.core.management.base import BaseCommand

from mainapp.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        i = 0
        unique_collisions = 0
        total = Document.objects.count()
        for doc in Document.objects.all().only("title", "source"):
            try:
                doc_dupe = Document.objects.exclude(id=doc.id).get(title=doc.title, source=doc.source)
            except:
                doc_dupe = None
            if doc_dupe:
                unique_collisions += 1
                print("Deleting duplicate", unique_collisions)
                doc.delete()
            i += 1
            if i % 100000 == 0:
                print(i, "/", total)
