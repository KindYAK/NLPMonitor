import os

import pandas as pd
from django.core.management.base import BaseCommand
from elasticsearch.helpers import parallel_bulk
import elasticsearch_dsl as es

from nlpmonitor.settings import MEDIA_ROOT, ES_CLIENT, ES_INDEX_CUSTOM_DICTIONARY_WORD
from mainapp.documents import CustomDictionaryWord


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.build_custom_dict()

    def word_generator(self, df):
        for index, row in df.iterrows():
            word = CustomDictionaryWord()
            word.word = row['word'] if type(row['word'] == str) else ""
            word.word_normal = row['word_normal'] if type(row['word_normal']) == str else ""
            yield word.to_dict()

    def build_custom_dict(self):
        df = pd.read_excel(os.path.join(MEDIA_ROOT, 'dict.xlsx'))
        number_of_words = len(df)

        index = es.Index(ES_INDEX_CUSTOM_DICTIONARY_WORD, using=ES_CLIENT)
        index.delete(ignore=404)
        print("Creating index")
        CustomDictionaryWord.init()

        failed, success = 0, 0
        batch_size = 1000
        for ok, result in parallel_bulk(ES_CLIENT, self.word_generator(df), index=ES_INDEX_CUSTOM_DICTIONARY_WORD,
                                        chunk_size=batch_size, raise_on_error=False, thread_count=6):
            if ok:
                success += 1
            else:
                failed += 1
                action, result = result.popitem()
                print("!!!", action, result)

            if failed > 3:
                raise Exception("Too many failed!!")
            if (success + failed) % batch_size == 0:
                print(f'{success+failed}/{number_of_words} processed')
