from typing import Dict

from django.core.management.base import BaseCommand
from django.db.models import Count

from fahrplandatengarten.core.models import (Source, Journey, JourneyStop)


class Command(BaseCommand):
    help = 'Fix/Merge Journeys which have multiple external IDs. This is only build for one time use to fix the bug. Because of this the code is not that nice.'

    def handle(self, *args, **options):
        source_db_hafas = Source.objects.get(internal_name="db_hafas")

        duplicated_journeys_datename = Journey.objects.filter(
            source=source_db_hafas,
        ).values('date', 'name').annotate(
            date_count=Count('date'), name_count=Count('name')
        ).filter(date_count__gt=1, name_count__gt=1)

        for duplicated_journey in duplicated_journeys_datename:
            journeystops: Dict[int, JourneyStop] = {}
            duplicated_journeys_data = Journey.objects.filter(
                date=duplicated_journey['date'],
                name=duplicated_journey['name']
            ).order_by('-id')
            for duplicated_journey_data in duplicated_journeys_data:
                duplicated_journeystops = JourneyStop.objects.filter(
                    journey=duplicated_journey_data,
                )
                for duplicated_journeystop in duplicated_journeystops:
                    try:
                        saved_journeystop: JourneyStop = journeystops[duplicated_journeystop.stop_id]
                        if saved_journeystop.actual_departure_delay is None:
                            saved_journeystop.actual_departure_delay = duplicated_journeystop.actual_departure_delay
                        if saved_journeystop.actual_arrival_delay is None:
                            saved_journeystop.actual_arrival_delay = duplicated_journeystop.actual_arrival_delay
                    except KeyError:
                        journeystops[duplicated_journeystop.stop_id] = duplicated_journeystop

            last_journey_journeystops = JourneyStop.objects.filter(
                journey=duplicated_journeys_data[0],
            )
            for last_journey_journeystop in last_journey_journeystops:
                last_journey_journeystop = journeystops[last_journey_journeystop.stop_id]
                last_journey_journeystop.save()
            duplicated_journeys_data.exclude(pk=duplicated_journeys_data[0].pk).delete()
