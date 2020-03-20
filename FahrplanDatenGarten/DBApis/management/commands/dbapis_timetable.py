# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from core.models import Stop
from DBApis.hafasImport import HafasImport


class Command(BaseCommand):
    help = 'Imports the Timetable from DB API'

    def add_arguments(self, parser):
        parser.add_argument('stopname', nargs='?', type=str)

    def handle(self, *args, **options):
        stop = Stop.objects.get(stopname__name=options['stopname'])
        hafasimport = HafasImport()
        hafasimport.import_timetable(stop)
