import pandas as pd
import os, json

from annoying.functions import get_object_or_None
from django.core.management.base import BaseCommand
from mainapp.models import *
from nlpmonitor.settings import MEDIA_ROOT


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.parse_csv()

    def parse_csv(self):
        corpus = get_object_or_None(Corpus, name="main")
        if not corpus:
            corpus = Corpus.objects.create(name="main")
        chunksize = 50000
        dfs = pd.read_csv(os.path.join(MEDIA_ROOT, '1.csv'), chunksize=chunksize)
        for i, df in enumerate(dfs, start=1):
            for index, row in df.iterrows():
                media_name = ""
                media_url = ""
                source = get_object_or_None(Source, name=media_name, corpus=corpus)
                if not source:
                    source = Source.objects.create(name=media_name, url=media_url, corpus=corpus)
                document = Document.objects.create()
                for tag_name in json.loads(""):
                    tag = get_object_or_None(Tag, name=tag_name, corpus=corpus)
                    if not tag:
                        tag = Tag.objects.create(name=tag_name, corpus=corpus)
                    document.tags.add(tag)
            print(i * chunksize)
