import datetime

import pytz
from django.core.management.base import BaseCommand
from core.models import Agency, Source, Stop, StopName, StopID, Journey, JourneyStop


class Command(BaseCommand):
    help = "Seeds (fake) data in database"

    def handle(self, *args, **options):
        agency = Agency.objects.update_or_create(name="DB")
        source = Source.objects.update_or_create(name="DBApis")
        stop = Stop.objects.update_or_create(ifopt="de:05315:11201")
        StopName.objects.update_or_create(stop=stop,
                                name="Köln Hbf",
                                source=source,
                                priority=1)
        StopID.objects.update_or_create(stop=stop, source_stop_id="8000207",
                              source=source, source_stop_id_type="EVA")
        journey = Journey.objects.create(name="ICE 557", date=datetime.datetime.now(),
                                         journey_id="123jd213/12312hd", source=source,
                                         agency=agency)
        JourneyStop.objects.create(stop=stop,
                                   journey=journey,
                                   planned_arrival_time=datetime.datetime(2019, 9, 12, 12, 00, tzinfo=pytz.utc),
                                   actual_arrival_time=datetime.datetime(2019, 9, 12, 17, 00, tzinfo=pytz.utc),
                                   planned_departure_time=datetime.datetime(2019, 9, 12, 13, 00, tzinfo=pytz.utc),
                                   actual_departure_time=datetime.datetime(2019, 9, 12, 20, 00, tzinfo=pytz.utc))
