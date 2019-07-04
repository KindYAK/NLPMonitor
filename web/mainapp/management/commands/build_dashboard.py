from django.core.management.base import BaseCommand
from elasticsearch_dsl import Search

from mainapp.models import *
from mainapp.models import Document as ModelDocument
from mainapp.documents import *
from mainapp.services import batch_qs, date_generator


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.tag_batch_size = 10000
        Dashboard.init()
        self.build_publications()

    def delete_ready_dashboards(self, type, tag=None):
        s = Search(using=ES_CLIENT, index=ES_INDEX_DASHOBARD)
        s = s.params(conflicts='proceed')
        s = s.filter("term", **{"type": type})
        s = s.filter("term", **{"is_ready": True})
        if tag:
            s = s.filter("term", **{"tag": tag})
        s.delete()

    def create_publications(self, qs, corpus, tag=None):
        dashboard_document = Dashboard(corpus=corpus.name,
                                       datetime_started=timezone.now(),
                                       type=DASHBOARD_TYPE_NUM_PUBLICATIONS_BY_TAG if tag else DASHBOARD_TYPE_NUM_PUBLICATIONS_OVERALL,
                                       granularity="1d",
                                       is_ready=False,
                                       tag=tag.name if tag else None
                                       )
        for date in date_generator(qs.earliest('datetime').datetime.date(), qs.latest('datetime').datetime.date()):
            dashboard_document.add_value(qs.filter(datetime__contains=date).count(), date)
        dashboard_document.datetime_generated = timezone.now()
        dashboard_document.is_ready = True
        self.delete_ready_dashboards(DASHBOARD_TYPE_NUM_PUBLICATIONS_BY_TAG if tag else DASHBOARD_TYPE_NUM_PUBLICATIONS_OVERALL,
                                     tag.name if tag else None)
        dashboard_document.save()

    def build_publications(self):
        for corpus in Corpus.objects.all():
            for tags in batch_qs(Tag.objects.filter(corpus=corpus), batch_size=self.tag_batch_size):
                for tag in tags:
                    ds = ModelDocument.objects.filter(tags=tag)
                    self.create_publications(ds, corpus, tag)
            self.create_publications(ModelDocument.objects.filter(source__corpus=corpus), corpus)
