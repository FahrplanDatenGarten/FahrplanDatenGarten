from core.models import Stop
from DBApis.hafasImport import HafasImport
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports the Timetable for a specific station'

    def add_arguments(self, parser):
        parser.add_argument(
            'stop_pk',
            type=int)

    def handle(self, *args, **options):
        hafasimport = HafasImport()
        hafasimport.import_timetable(Stop.objects.get(pk=options['stop_pk']), duration=900)
