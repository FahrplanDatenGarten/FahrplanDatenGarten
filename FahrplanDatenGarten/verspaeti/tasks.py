import datetime

from celery.schedules import crontab
from celery.task import periodic_task
from django.core.cache import cache

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

    delayed_stops = JourneyStop.objects.filter(
        journey__in=current_journeys,
        actual_departure_delay__gte=datetime.timedelta(minutes=5)).order_by('-actual_departure_delay')

    cache.set("verspaeti_data", {
        "num_current_journeys": current_journeys.count(),
        "num_delayed_journeys": len({d.journey.name for d in delayed_stops}),
        "biggest_delay": delayed_stops[0] if len(delayed_stops) else 0,
        "biggest_delay_time": int(delayed_stops[0].actual_departure_delay.seconds / 60) if len(delayed_stops) else 0,
        "average_delay": round((sum([d.actual_departure_delay.seconds / 60 for d in delayed_stops]) / len(
            delayed_stops))) if delayed_stops else None
    }, 45 * 60)
