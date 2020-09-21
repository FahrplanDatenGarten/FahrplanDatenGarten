import datetime
from typing import List, Tuple

from celery.schedules import crontab
from celery.task import periodic_task
from django.core.cache import cache
from django.db.models import Avg

from core.models import Journey, JourneyStop


@periodic_task(
    run_every=crontab(
        hour="*",
        minute="*/30"),
    name="verspaeti_statistics",
    ignore_result=True)
def verspaeti_statistics():
    current_journeys = Journey.objects.filter(
        journeystop__planned_arrival_time__gte=datetime.datetime.now() - datetime.timedelta(days=1)
    ).distinct().all()

    all_journey_delays: List[datetime.timedelta] = []
    delayed_journey_delays: List[Tuple[int, datetime.timedelta]] = []

    for journey in current_journeys:
        aggregated_journey_stops = JourneyStop.objects.filter(
            journey=journey
        ).aggregate(Avg('actual_arrival_delay'))
        if aggregated_journey_stops['actual_arrival_delay__avg'] is not None:
            all_journey_delays.append(aggregated_journey_stops['actual_arrival_delay__avg'])
            if aggregated_journey_stops['actual_arrival_delay__avg'] > datetime.timedelta(minutes=5):
                delayed_journey_delays.append((journey.pk, aggregated_journey_stops['actual_arrival_delay__avg']))

    sorted_delayed_journey_delays = sorted(delayed_journey_delays, key=lambda x: x[1], reverse=True)
    cache.set("verspaeti_data", {
        "num_current_journeys": current_journeys.count(),
        "num_delayed_journeys": len(delayed_journey_delays),
        "biggest_delay_name": Journey.objects.get(pk=sorted_delayed_journey_delays[0][0]).name if delayed_journey_delays else 0,
        "biggest_delay_time": round(sorted_delayed_journey_delays[0][1].seconds / 60) if len(delayed_journey_delays) else 0,
        "average_delay": round(
            (sum(all_journey_delays, datetime.timedelta(0)) / len(all_journey_delays)).seconds / 60) if delayed_journey_delays else None
    }, 45 * 60)
