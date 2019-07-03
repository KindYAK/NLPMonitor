from django.core.management.base import BaseCommand

from mainapp.models import *
from mainapp.models import Document as ModelDocument
from mainapp.documents import *
from mainapp.services import batch_qs, date_generator


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.tag_batch_size = 10000
        Dashboard.init()
        self.build_publications_by_tag()

    def build_publications_by_tag(self):
        for corpus in Corpus.objects.all():
            for tags in batch_qs(Tag.objects.filter(corpus=corpus), batch_size=self.tag_batch_size):
                for tag in tags:
                    ds = ModelDocument.objects.filter(tags=tag).only('datetime')
                    dashboard_document = Dashboard(corpus=corpus.name,
                                                   type=DASHBOARD_TYPE_NUM_PUBLICATIONS_BY_TAG,
                                                   granularity="1d",
                                                   is_ready=False,
                                                   tag=tag.name
                                                   )
                    for date in date_generator(ds.earliest('datetime').datetime.date(), ds.latest('datetime').datetime.date()):
                        dashboard_document.add_value(ds.filter(datetime__date=date).count(), date)
                    dashboard_document.save()
