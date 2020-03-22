# -*- coding: utf-8 -*-

import csv
import io

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from core.models import Agency, Source, Stop, StopID, StopIDKind, StopName, StopLocation

from pyhafas import HafasClient
from pyhafas.profile import DBProfile


class Command(BaseCommand):
    help = 'Imports the Stations from the Haltestellendaten-CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv-url',
            nargs='?',
            type=str,
            default='http://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV')

    def handle(self, *args, **options):
        hafasClient = HafasClient(DBProfile())
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
            if row['EVA_NR'] == '':
                continue
            stop = Stop.objects.filter(
                stopid__name=row['EVA_NR'],
                stopid__kind__in=agency.used_id_kind.all()
            ).first()
            if stop is None:
                stop = Stop()
                stop.save()
            StopName.objects.get_or_create(
                name=row['NAME'], stop=stop, source=source)
            StopID.objects.get_or_create(
                stop=stop,
                name=row['EVA_NR'],
                source=source,
                kind=kind
            )
            try:
                StopLocation.objects.get(
                    stop=stop,
                    source=source
                )
            except ObjectDoesNotExist:
                try:
                    hafasLocation = hafasClient.locations(row['EVA_NR'])[0]
                    StopLocation.objects.create(
                        stop=stop,
                        latitude=hafasLocation.latitude,
                        longitude=hafasLocation.longitude,
                        source=source
                    )
                except IndexError:
                    continue
