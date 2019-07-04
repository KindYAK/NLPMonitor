from django.core.management.base import BaseCommand
from django.db.models import Sum
from elasticsearch_dsl import Search

from mainapp.dashboard_types import *
from mainapp.documents import *
from mainapp.models import Document as ModelDocument, Corpus, Tag
from mainapp.services import batch_qs, date_generator


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.tag_batch_size = 10000
        Dashboard.init()
        for dashboard_type in list(filter(lambda x: x['filtering'] == FILTERING_TYPE_BY_TAG, DASHBOARD_TYPES)):
            self.build_dashboard_by_tag(dashboard_type)
        for dashboard_type in list(filter(lambda x: x['filtering'] == FILTERING_TYPE_OVERALL, DASHBOARD_TYPES)):
            self.build_dashboard_overall(dashboard_type)

    def delete_ready_dashboards(self, dashboard_type, tag=None):
        s = Search(using=ES_CLIENT, index=ES_INDEX_DASHOBARD)
        s = s.params(conflicts='proceed')
        s = s.filter("term", **{"type": dashboard_type['type']})
        s = s.filter("term", **{"is_ready": True})
        if tag:
            s = s.filter("term", **{"tag": tag})
        s.delete()

    def create_dashboard(self, qs, dashboard_type, corpus, tag=None):
        dashboard_document = Dashboard(corpus=corpus.name,
                                       datetime_started=timezone.now(),
                                       type=dashboard_type['type'],
                                       granularity="1d",
                                       is_ready=False,
                                       tag=tag.name if tag else None
                                       )
        for date in date_generator(qs.earliest('datetime').datetime.date(), qs.latest('datetime').datetime.date()):
            if dashboard_type['value'] == VALUE_TYPE_COUNT:
                value = qs.filter(datetime__contains=date).count()
            elif dashboard_type['value'] == VALUE_TYPE_SUM:
                value = qs.filter(datetime__contains=date)\
                    .aggregate(Sum(dashboard_type['field']))[f"{dashboard_type['field']}__sum"]
            else:
                raise Exception("Value type not implemented")
            dashboard_document.add_value(value, date)
        dashboard_document.datetime_generated = timezone.now()
        dashboard_document.is_ready = True
        self.delete_ready_dashboards(dashboard_type, tag.name if tag else None)
        dashboard_document.save()

    def build_dashboard_by_tag(self, dashboard_type):
        for corpus in Corpus.objects.all():
            for tags in batch_qs(Tag.objects.filter(corpus=corpus), batch_size=self.tag_batch_size):
                for tag in tags:
                    ds = ModelDocument.objects.filter(tags=tag)
                    self.create_dashboard(ds, dashboard_type, corpus, tag)

    def build_dashboard_overall(self, dashboard_type):
        for corpus in Corpus.objects.all():
            ds = ModelDocument.objects.filter(source__corpus=corpus)
            self.create_dashboard(ds, dashboard_type, corpus)
