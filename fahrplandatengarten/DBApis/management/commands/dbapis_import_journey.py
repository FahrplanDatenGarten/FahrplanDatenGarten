from fahrplandatengarten.core.models import Journey
from fahrplandatengarten.DBApis.hafasImport import HafasImport
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Imports the specified journey'

    def add_arguments(self, parser):
        parser.add_argument(
            'journey_pk',
            type=int)

    def handle(self, *args, **options):
        hafasimport = HafasImport()
        hafasimport.import_journey(Journey.objects.get(pk=options['journey_pk']))
