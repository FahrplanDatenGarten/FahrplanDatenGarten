# -*- coding: utf-8 -*-

import csv
import io

import requests
from django.core.management.base import BaseCommand


from DBApis.tasks import dbapis_importstations_parse_station_row
from core.models import Agency, Source, StopIDKind


class Command(BaseCommand):
    help = 'Imports the Stations from the Haltestellendaten-CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv-url',
            nargs='?',
            type=str,
            default='http://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV')

    def handle(self, *args, **options):
        agency, _ = Agency.objects.get_or_create(name="db")
        source, _ = Source.objects.get_or_create(name="dbapis")
        kind, _ = StopIDKind.objects.get_or_create(name='eva')

        agency.used_id_kind.add(kind)
        agency.save()

        r = requests.get(options.get('csv-url'))
        r.encoding = 'utf-8'
        csv_string = r.text
        csv_file = io.StringIO()
        csv_file.write(csv_string)
        csv_file.seek(0)
        reader = csv.DictReader(csv_file, delimiter=';')
        for row in reader:
            dbapis_importstations_parse_station_row.delay(row, agency.pk, source.pk, kind.pk)
