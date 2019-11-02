# -*- coding: utf-8 -*-

import csv
import io

import requests
from django.core.management.base import BaseCommand, CommandError

from core.models import Agency, Source, Stop, StopID, StopIDKind, StopName, StopLocation


class Command(BaseCommand):
    help = 'Imports the Stations from the Trainline-CSV'
    # TODO: Replace missing id-names
    operators = {
        'sncf': ['sncf'],
        'sncf_tvs': ['sncf_tvs'],
        'idtgv': ['idtgv'],
        'db': ['eva'],
        'hkx': ['hkx'],
        'busbud': ['busbud'],
        'distribusion': ['distribusion'],
        'flixbus': ['flixbus'],
        'leoexpress': ['leoexpress'],
        'cff': ['cff'],
        'obb': ['obb'],
        'ouigo': ['ouigo'],
        'trenitalia': ['trenitalia'],
        'trenitalia_rtvt': ['trenitalia_rtvt'],
        'ntv': ['ntv'],
        'ntv_rtiv': ['ntv_rtiv'],
        'hkx': ['hkx'],
        'renfe': ['renfe'],
        'atoc': ['atoc'],
        'benerail': ['benerail'],
        'westbahn': ['westbahn'],
    }

    def add_arguments(self, parser):
        parser.add_argument('csv-url', nargs='?', type=str, default='https://raw.githubusercontent.com/trainline-eu/stations/master/stations.csv')

    def handle(self, *args, **options):
        trainline, _ = Source.objects.get_or_create(name="trainline")

        r = requests.get(options.get('csv-url'))
        r.encoding = 'utf-8'
        csv_string = r.text
        csv_file = io.StringIO()
        csv_file.write(csv_string)
        csv_file.seek(0)
        reader = csv.DictReader(csv_file, delimiter=';')

        first_row = True
        stop_objs = []
        stopid_objs = []
        stopname_objs = []
        stoplocation_objs = []
        row_counter = 0
        for row in reader:
            if first_row:
                # Create all agencies from the imported CSV.
                angency_objs = []
                agencies = []
                for key in row.keys():
                    if key[-3:] == '_id' and not key in ['parent_station_id']:
                        name = key[:-3]
                        agency = Agency.objects.filter(name=name).first()

                        if agency is None:
                            agency = Agency(name=name)
                            agency.save()
                        agencies.append(agency)

                # Import the StopIDKinds
                primary_id_kinds = {}
                for agency in agencies:
                    for idkind_name in self.operators[agency.name]:
                        idkind = StopIDKind.objects.filter(name=idkind_name).first()
                        if idkind is None:
                            idkind = StopIDKind(name=idkind_name)
                            idkind.save()
                        agency.used_id_kind.add(idkind)

                        if idkind_name == self.operators[agency.name][0]:
                            primary_id_kinds[agency.name] = idkind
                uic_kind , _ = StopIDKind.objects.get_or_create(name='uic')
                first_row = False


            # Now import all stops from the CSV
            ids = {}
            stop = None
            for agency in agencies:
                id = row.get('{}_id'.format(agency.name))
                if not (id is None or id == ''):
                    ids[agency.name] = id
                    if stop is None:
                        stop = Stop.objects.filter(
                            stopid__name=id,
                            stopid__kind__in=agency.used_id_kind.all()
                        ).first()
            if stop is None:
                stop = Stop()
                stop.save()

            if not row.get('uic', '') == '':
                stopid_objs.append(StopID(name=row.get('uic'), stop=stop, kind=uic_kind, source=trainline))

            for id_name in ids.keys():
                stopid_obj = StopID(
                    name=ids[id_name],
                    stop=stop,
                    source=trainline,
                    kind=primary_id_kinds[id_name]
                )
                stopid_objs.append(stopid_obj)
            if not (row.get('latitude', '') == '' or row.get('longitude', '') == ''):
                stoplocation_objs.append(StopLocation(
                    latitude=row.get('latitude'),
                    longitude=row.get('longitude'),
                    source=trainline,
                    stop=stop
                ))

            stopname_objs.append(StopName(
                name=row.get('name'),
                source=trainline,
                stop=stop
            ))

            if row_counter % 100 == 0:
                Stop.objects.bulk_create(stop_objs)
                StopName.objects.bulk_create(stopname_objs)
                StopLocation.objects.bulk_create(stoplocation_objs)
                StopID.objects.bulk_create(stopid_objs)

                stop_objs = []
                stopid_objs = []
                stopname_objs = []
                stoplocation_objs = []

            row_counter += 1

        print('Writing Data to Database')
        Stop.objects.bulk_create(stop_objs)
        StopID.objects.bulk_create(stopid_objs)
        StopName.objects.bulk_create(stopname_objs)
        StopLocation.objects.bulk_create(stoplocation_objs)
