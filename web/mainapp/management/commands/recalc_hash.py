import pandas as pd
import os, json, datetime, pytz, math

from annoying.functions import get_object_or_None
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from mainapp.models import *
from nlpmonitor.settings import MEDIA_ROOT


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 0
        for doc in Document.objects.all():
            try:
                doc.save()
            except Exception as e:
                print("!!!", e)
                print("Deleting duplicate")
                doc.delete()
            if not doc.unique_hash:
                print("Not hash", doc.id)
            i += 1
            if i % 10000 == 0:
                print(i, "/", Document.objects.count())
