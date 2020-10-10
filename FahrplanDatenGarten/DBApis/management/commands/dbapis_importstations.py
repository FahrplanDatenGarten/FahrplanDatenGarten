from core.models import Provider, Source, StopIDKind
from DBApis.csvImport import parse_db_opendata_stop_csv
from DBApis.tasks import dbapis_importstations_parse_station_row
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports the Stations from the Haltestellendaten-CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv-url',
            nargs='?',
            type=str,
            default='http://download-data.deutschebahn.com/static/datasets/haltestellen/D_Bahnhof_2020_alle.CSV')

    def handle(self, *args, **options):
        provider, _ = Provider.objects.get_or_create(
            internal_name="db", friendly_name="Deutsche Bahn")
        source, _ = Source.objects.get_or_create(
            internal_name="db_csv",
            friendly_name="DB Open-Data-Portal CSV",
            provider=provider)
        kind, _ = StopIDKind.objects.get_or_create(
            name='eva', provider=provider)

        csv_reader = parse_db_opendata_stop_csv()
        for row in csv_reader:
            dbapis_importstations_parse_station_row.delay(
                row, provider.pk, source.pk, kind.pk)
