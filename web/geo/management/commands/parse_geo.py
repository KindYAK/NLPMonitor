import os

import pandas as pd
from django.core.management.base import BaseCommand

from geo.models import Locality, Area, District
from nlpmonitor.settings import MEDIA_ROOT


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.parse_csv()

    def parse_csv(self):
        df = pd.read_excel(os.path.join(MEDIA_ROOT, 'geo.xlsx'))

        print('Parsing Areas ...')
        areas_dict = {area: Area(name=area) for area in df['Область'].unique().tolist()}
        Area.objects.bulk_create(areas_dict.values())

        print('Parsing Districts ...')
        districts_dict = {
            district: District(name=district, area=areas_dict[df[df['Район'] == district]['Область'].unique()[0]])
            for district in df['Район'].unique().tolist()
        }
        District.objects.bulk_create(districts_dict.values())

        print('Parsing Localities:')
        localities_list = list()
        longitude, latitude = df['Координаты'][0].split(', ')
        for row in df.iterrows():

            if isinstance(row[1]['Координаты'], str):
                longitude, latitude = row[1]['Координаты'].split(', ')

            localities_list.append(
                Locality(name=row[1]['Населенный пункт'],
                         kato_code=row[1]['Код КАТО'],
                         longitude=longitude,
                         latitude=latitude,
                         district=districts_dict[row[1]['Район']])
            )

            if row[0] % 1000 == 0:
                print(f'  Parsed - {row[0]} rows')

        Locality.objects.bulk_create(localities_list, ignore_conflicts=True)
