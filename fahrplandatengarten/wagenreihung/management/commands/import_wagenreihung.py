from django.core.management.base import BaseCommand

from fahrplandatengarten.core.models import JourneyStop
from wagenreihung.istWrClient import IstWrClient


class Command(BaseCommand):
    help = 'Imports the Wagenriehung for a specified journey and stop'

    def add_arguments(self, parser):
        parser.add_argument(
            'journey_pk',
            type=int)
        parser.add_argument(
            'stop_pk',
            type=int)

    def handle(self, *args, **options):
        js = JourneyStop.objects.get(journey__pk=options['journey_pk'], stop__pk=options['stop_pk'])
        istWrClient = IstWrClient(js)
        istWrClient.import_wr()
