# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from DBApis.hafasImport import HafasImport
from core.models import Journey

class Command(BaseCommand):
    help = 'Imports the Timetable from DB API'

    def add_arguments(self, parser):
        parser.add_argument('journeyid', nargs='?', type=str)

    def handle(self, *args, **options):
        stop = Journey.objects.filter(journey_id=options['journeyid']).first()
        hafasimport = HafasImport()
        hafasimport.import_journey(stop)
