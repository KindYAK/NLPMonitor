from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from mainapp.models import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        unique_collisions = 0
        for doc in Document.objects.all():
            try:
                doc.save()
            except IntegrityError as e:
                unique_collisions += 1
                print("!!!", e)
                print("Deleting duplicate", unique_collisions)
                doc.delete()
            except Exception as e:
                print("!!!!!!!!!! ANOTHER EXCEPTION", e)
            if not doc.unique_hash:
                print("Not hash", doc.id)
            i += 1
            if i % 100000 == 0:
                print(i, "/", Document.objects.count())
