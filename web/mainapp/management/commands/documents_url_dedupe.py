import datetime
from collections import defaultdict

from django.core.management.base import BaseCommand

from mainapp.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        i = 0
        unique_collisions = 0
        qs = Document.objects.exclude(url=None)
        total = qs.count()
        url_ids_dict = defaultdict(set)
        print("!!!", "Getting url_ids_dict", datetime.datetime.now())
        for doc in qs.only("url"):
            url_ids_dict[doc.url.strip()].add(doc.id)
            i += 1
            if i % 100000 == 0:
                print(i, "/", total, "to dict", datetime.datetime.now())

        for ids in url_ids_dict.values():
            ids_to_delete = list(ids)[1:]
            if not ids_to_delete:
                continue
            unique_collisions += len(ids_to_delete)
            Document.objects.filter(id__in=ids_to_delete).delete()
            if unique_collisions % 10000 == 0:
                print("Deleting duplicate", unique_collisions)