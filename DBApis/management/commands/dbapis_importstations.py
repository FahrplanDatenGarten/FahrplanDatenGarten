# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from core.models import Stop, StopID, StopIDKind, StopName, Source, Agency
import csv
import io
import requests

class Command(BaseCommand):
    help = 'Imports the Stations from the Haltestellendaten-CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv-url', nargs='?', type=str, default='http://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2017_09.csv')

    def handle(self, *args, **options):
        agency, _ = Agency.objects.get_or_create(name="db")
        source, _ = Source.objects.get_or_create(name="dbapis")

        r = requests.get(options.get('csv-url'))
        r.encoding = 'utf-8'
        csv_string = r.text
        csv_file = io.StringIO()
        csv_file.write(csv_string)
        csv_file.seek(0)
        reader = csv.DictReader(csv_file, delimiter=';')
        for row in reader:
            if row['\ufeffEVA_NR'] is '':
                continue
            stop = Stop.objects.filter(
                stopid__name=row['\ufeffEVA_NR'],
                stopid__kind__in=agency.used_id_kind.all()
            ).first()
            if stop is None:
                stop = Stop()
                stop.save()
            StopName.objects.get_or_create(name=row['NAME'], stop=stop, source=source)
            StopID.objects.get_or_create(
                stop=stop,
                name=row['\ufeffEVA_NR'],
                source=source,
                kind=StopIDKind.objects.filter(
                    name='eva'
                ).first()
            )
