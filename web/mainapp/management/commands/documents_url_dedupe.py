from django.core.management.base import BaseCommand

from mainapp.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        i = 0
        unique_collisions = 0
        total = Document.objects.count()
        for doc in Document.objects.all().only("url"):
            doc_dupe = Document.objects.exclude(id=doc.id).filter(url=doc.url)
            for d in doc_dupe:
                unique_collisions += 1
                if unique_collisions % 10000 == 0:
                    print("Deleting duplicate", unique_collisions)
                d.delete()
            i += 1
            if i % 100000 == 0:
                print(i, "/", total)
