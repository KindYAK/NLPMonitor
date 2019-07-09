import pandas as pd
import os, json, datetime, pytz, math

from annoying.functions import get_object_or_None
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from mainapp.models import *
from nlpmonitor.settings import MEDIA_ROOT


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.parse_csv()

    def parse_csv(self):
        Tag.objects.all().delete()
        corpus = get_object_or_None(Corpus, name="main")
        df = pd.read_csv(os.path.join(MEDIA_ROOT, '1.csv'), index_col=0)
        df = df[pd.notnull(df['tags'])]
        passed = 0
        for index, row in df.iterrows():
            media_name = row['mass_media_name']
            source = get_object_or_None(Source, name=media_name, corpus=corpus)
            if not source:
                continue

            author_name = row['author']
            author = None
            if author_name and type(author_name) == str:
                author = get_object_or_None(Author, name=author_name, corpus=corpus)
                if not author:
                    continue

            date = None
            if row['date'] and type(row['date']) == str:
                try:
                    date = datetime.datetime.strptime(row['date'], "%Y-%m-%d")
                except:
                    try:
                        date = datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S")
                    except:
                        date = datetime.datetime.strptime(row['date'], "%Y-%m-%d %H:%M:%S.%f")
                date = date.replace(tzinfo=pytz.timezone('Asia/Almaty'))

            if not row['title'] or type(row['title']) != str:
                continue

            if not row['text'] or type(row['text']) != str or not row['text'] or type(row['text']) != str:
                continue

            try:
                document = get_object_or_None(Document, source=source, datetime=date, title=row['title'])
            except:
                passed += 1
                continue
            if document and row['tags'] and type(row['tags']) == str:
                for tag_name in json.loads(row['tags']):
                    tag = get_object_or_None(Tag, name=tag_name[:Tag._meta.get_field('name').max_length], corpus=corpus)
                    if not tag:
                        tag = Tag.objects.create(name=tag_name[:Tag._meta.get_field('name').max_length], corpus=corpus)
                    document.tags.add(tag)
        print("Passed:", passed)
