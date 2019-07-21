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
        corpus = get_object_or_None(Corpus, name="main")
        if not corpus:
            corpus = Corpus.objects.create(name="main")
        chunksize = 50000
        db_chunksize = 10000
        dfs = pd.read_csv(os.path.join(MEDIA_ROOT, '1.csv'), index_col=0, chunksize=chunksize, skiprows=range(1, 1500000))
        documents = []
        for i, df in enumerate(dfs, start=1):
            for index, row in df.iterrows():
                media_name = row['mass_media_name']
                source = get_object_or_None(Source, name=media_name, corpus=corpus)
                if not source:
                    source = Source.objects.create(name=media_name, url=media_name, corpus=corpus)

                author_name = row['author']
                author = None
                if author_name and type(author_name) == str:
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
                                    text=row['text'] if type(row['text']) == str else None,
                                    html=row['html'] if type(row['html']) == str else None,
                                    title=row['title'][:Document._meta.get_field('title').max_length] if type(row['title']) == str else None,
                                    url=row['url'] if type(row['url']) == str else None,
                                    links=row['links'] if type(row['links']) == str else None,
                                    num_comments=int(row['num_coms']) if row['num_coms'] and not math.isnan(row['num_coms']) else None,
                                    num_views=int(row['views']) if row['views'] and not math.isnan(row['views']) else None,
                                    )
                if not (row['tags'] and type(row['tags']) == str) and not(row['topic'] and type(row['topic']) == str):
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
                        tag = get_object_or_None(Tag, name=tag_name[:Tag._meta.get_field('name').max_length], corpus=corpus)
                        if not tag:
                            tag = Tag.objects.create(name=tag_name[:Tag._meta.get_field('name').max_length], corpus=corpus)
                        document.tags.add(tag)

                topic_name = row['topic']
                if topic_name and type(topic_name) == str:
                    topic = get_object_or_None(Category, name=topic_name[:Category._meta.get_field('name').max_length], corpus=corpus)
                    if not topic:
                        topic = Category.objects.create(name=topic_name[:Category._meta.get_field('name').max_length], corpus=corpus)
                    document.categories.add(topic)
            print(i * chunksize)
        Document.objects.bulk_create(documents, ignore_conflicts=True)
