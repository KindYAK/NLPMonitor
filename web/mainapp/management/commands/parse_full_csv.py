import datetime
import json
import math
import os
import pytz

import pandas as pd
from annoying.functions import get_object_or_None
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from mainapp.models import *
from nlpmonitor.settings import MEDIA_ROOT


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-c', '--corpus_name', type=str)
        parser.add_argument('-f', '--filename', type=str)

    def handle(self, *args, **options):
        self.corpus_name = options['corpus_name']
        self.filename = options['filename']
        self.parse_csv()

    @staticmethod
    def row_str_parser(row, param_name):
        return row[param_name] if (param_name in row) and (type(row[param_name]) == str) else None

    @staticmethod
    def row_int_parser(row, param_name):
        return int(row[param_name]) if (param_name in row) and (row[param_name]) and (not math.isnan(row[param_name])) else None

    def parse_csv(self):
        max_len = Document._meta.get_field('title').max_length
        corpus = get_object_or_None(Corpus, name=self.corpus_name)
        if not corpus:
            corpus = Corpus.objects.create(name=self.corpus_name)
        chunksize = 50000
        db_chunksize = 10000
        dfs = pd.read_csv(os.path.join(MEDIA_ROOT, self.filename), chunksize=chunksize)
        documents = []
        for i, df in enumerate(dfs, start=1):
            for index, row in df.iterrows():
                media_name = row['mass_media_name']
                source = get_object_or_None(Source, name=media_name, corpus=corpus)
                if not source:
                    source = Source.objects.create(name=media_name, url=media_name, corpus=corpus)

                author = None
                if "author" in row:
                    author_name = row['author']
                    if author_name and type(author_name) == str:
                        author_name = author_name[:200]
                        author = get_object_or_None(Author, name=author_name, corpus=corpus)
                        if not author:
                            author = Author.objects.create(name=author_name, corpus=corpus)

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

                if not row['text'] or type(row['text']) != str:
                    continue

                if Document.objects.filter(source=source, datetime=date, title=row['title']).exists() or not row['text'] or type(row['text']) != str:
                    continue
                document = Document(source=source,
                                    author=author,
                                    datetime=date,
                                    text=self.row_str_parser(row, 'text'),
                                    html=self.row_str_parser(row, 'html'),
                                    title=self.row_str_parser(row, 'title')[:max_len] if self.row_str_parser(row, 'title') else None,
                                    url=self.row_str_parser(row, 'url'),
                                    links=self.row_str_parser(row, 'links'),
                                    num_comments=self.row_int_parser(row, 'num_comments'),
                                    num_views=self.row_int_parser(row, 'num_views'),
                                    )

                if ('tags' not in row) or (not (row['tags'] and type(row['tags']) == str) and not (
                        row['topic'] and type(row['topic']) == str)):
                    documents.append(document)
                    if len(documents) % db_chunksize == 0:
                        Document.objects.bulk_create(documents, ignore_conflicts=True)
                        documents = []
                    continue
                try:
                    document.save()
                except IntegrityError as e:
                    if not "Duplicate" in str(e):
                        raise e
                    else:
                        continue
                if row['tags'] and type(row['tags']) == str:
                    for tag_name in json.loads(row['tags']):
                        tag = get_object_or_None(Tag, name=tag_name[:Tag._meta.get_field('name').max_length],
                                                 corpus=corpus)
                        if not tag:
                            tag = Tag.objects.create(name=tag_name[:Tag._meta.get_field('name').max_length],
                                                     corpus=corpus)
                        document.tags.add(tag)

                topic_name = row['topic']
                if topic_name and type(topic_name) == str:
                    topic = get_object_or_None(Category, name=topic_name[:Category._meta.get_field('name').max_length],
                                               corpus=corpus)
                    if not topic:
                        topic = Category.objects.create(name=topic_name[:Category._meta.get_field('name').max_length],
                                                        corpus=corpus)
                    document.categories.add(topic)
            print(i * chunksize)
        Document.objects.bulk_create(documents, ignore_conflicts=True)
