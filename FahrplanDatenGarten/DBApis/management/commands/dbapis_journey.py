# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from core.models import Journey
from DBApis.hafasImport import HafasImport


class Command(BaseCommand):
    help = 'Imports the Timetable from DB API'

    def add_arguments(self, parser):
        parser.add_argument('journeyid', nargs='?', type=str)

    def handle(self, *args, **options):
        hafasimport = HafasImport()

        stop = Journey.objects.filter(journey_id=options['journeyid']).first()
        if stop is not None:
            hafasimport.import_journey(stop)
        else:
            for journey in Journey.objects.filter(agency__name='db').all():
                hafasimport.import_journey(journey)
