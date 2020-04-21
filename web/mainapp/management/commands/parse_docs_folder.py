import os

from annoying.functions import get_object_or_None
from django.core.management.base import BaseCommand

from mainapp.models import *
from nlpmonitor.settings import MEDIA_ROOT


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--corpus', type=str, help='Corpus name')
        parser.add_argument('-f', '--folder', type=str, help='Folder to read from')

    def handle(self, *args, **options):
        corpus_name = options['corpus']
        folder_name = options['folder']
        self.parse_csv(corpus_name, folder_name)

    def parse_csv(self, corpus_name, folder_name):
        corpus = get_object_or_None(Corpus, name=corpus_name)
        if not corpus:
            corpus = Corpus.objects.create(name=corpus_name)
        db_chunksize = 10000
        documents = []
        i = 0
        file_list = os.walk(os.path.join(MEDIA_ROOT, folder_name))
        for dirpath, dirnames, filenames in file_list:
            for file in filenames:
                if i % 100 == 0:
                    print(f"{i}")
                i += 1
                media_name = "Гос программа"
                source = get_object_or_None(Source, name=media_name, corpus=corpus)
                if not source:
                    source = Source.objects.create(name=media_name, url=media_name, corpus=corpus)
                with open(os.path.join(MEDIA_ROOT, folder_name, file), "r") as f:
                    text = f.read()
                title = file[:Document._meta.get_field('title').max_length]
                title = ".".join(title.split(".")[:-1])
                document = Document(source=source,
                                    text=text,
                                    title=title
                )
                documents.append(document)
                if len(documents) % db_chunksize == 0:
                    Document.objects.bulk_create(documents, ignore_conflicts=True)
                    documents = []
        Document.objects.bulk_create(documents, ignore_conflicts=True)
