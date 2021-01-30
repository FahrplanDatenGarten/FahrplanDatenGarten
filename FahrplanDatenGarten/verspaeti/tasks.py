import base64
import datetime
from io import BytesIO
from typing import List, Tuple

from celery.schedules import crontab
from django.core.cache import cache
from django.db.models import Avg
from matplotlib import pyplot

from core.models import Journey, JourneyStop
from FahrplanDatenGarten.celery import app


@app.on_after_finalize.connect
def setup_dbapis_configure_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(
            hour="*",
            minute="*/30"),
        verspaeti_statistics.s()
    )


@app.task(name="verspaeti_statistics", ignore_result=True)
def verspaeti_statistics():
    current_journeys = Journey.objects.filter(
        journeystop__planned_arrival_time__gte=datetime.datetime.now() -
        datetime.timedelta(
            days=1)).distinct().all()
    all_journey_delays: List[datetime.timedelta] = []
    delayed_journey_delays: List[Tuple[int, datetime.timedelta]] = []

    for journey in current_journeys:
        aggregated_journey_stops = JourneyStop.objects.filter(
            journey=journey
        ).aggregate(Avg('actual_arrival_delay'))
        if aggregated_journey_stops['actual_arrival_delay__avg'] is not None:
            all_journey_delays.append(
                aggregated_journey_stops['actual_arrival_delay__avg'])
            if aggregated_journey_stops['actual_arrival_delay__avg'] > datetime.timedelta(
                    minutes=5):
                delayed_journey_delays.append(
                    (journey.pk, aggregated_journey_stops['actual_arrival_delay__avg']))

    sorted_delayed_journey_delays = sorted(
        delayed_journey_delays, key=lambda x: x[1], reverse=True)
    num_delayed_journeys = len(delayed_journey_delays)
    num_current_journeys = current_journeys.count()

    colors = ('#63a615', '#ec0016')
    labels = ('Pünktlich', 'Zu spät')
    values = [
        num_current_journeys -
        num_delayed_journeys,
        num_delayed_journeys]
    plot_figure, plot_axes = pyplot.subplots(figsize=(5, 6))
    plot_figure.subplots_adjust(bottom=0.3, top=0.95)

    plot_wedges, _, plot_autotexts = pyplot.pie(
        values,
        colors=colors,
        autopct='%1.1f%%')

    plot_axes.legend(
        plot_wedges,
        labels,
        loc="lower center",
        fontsize="xx-large",
        bbox_to_anchor=(0.5, -.3)
    )
    pyplot.setp(plot_autotexts, size=20)
    pyplot.axis('equal')
    plot_temporary_file = BytesIO()
    pyplot.savefig(plot_temporary_file, format='png', transparent=True)

    cache.set(
        "verspaeti_data", {
            "num_current_journeys": num_current_journeys,
            "num_delayed_journeys": num_delayed_journeys,
            "biggest_delay_name": Journey.objects.get(
                pk=sorted_delayed_journey_delays[0][0]).name if delayed_journey_delays else 0,
            "biggest_delay_time": round(
                sorted_delayed_journey_delays[0][1].seconds /
                60) if len(delayed_journey_delays) else 0,
            "average_delay": round(
                (sum(
                    all_journey_delays,
                    datetime.timedelta(0)) /
                 len(all_journey_delays)).seconds /
                60) if delayed_journey_delays else None,
            "plot_image_base64": base64.b64encode(
                plot_temporary_file.getvalue()).decode('utf-8')},
        2700)
