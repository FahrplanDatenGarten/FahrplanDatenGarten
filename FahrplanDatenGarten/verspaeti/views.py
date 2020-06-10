import datetime

from django.views.generic import TemplateView
from plotly.graph_objs import Pie
from plotly.offline import plot

from core import models


class IndexView(TemplateView):
    template_name = "verspaeti/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_journeys = models.Journey.objects.filter(
            journeystop__planned_arrival_time__gte=datetime.datetime.now() - datetime.timedelta(days=1)
        ).distinct().all()

        delayed_stops = models.JourneyStop.objects.filter(
            journey__in=current_journeys,
            actual_departure_delay__gte=datetime.timedelta(minutes=5)).order_by('-actual_departure_delay')
        num_delayed_journeys = len({d.journey.name for d in delayed_stops})

        colors = ['#63a615', '#ec0016']
        labels = ['Pünktlich', 'Zu spät']
        values = [
            current_journeys.count() -
            num_delayed_journeys,
            num_delayed_journeys]
        plot_div = plot([Pie(labels=labels, values=values,
                             marker=dict(colors=colors))], output_type='div')

        context['plot_div'] = plot_div
        context['current_journeys'] = current_journeys.count()
        context['journeys_delayed'] = num_delayed_journeys,
        context['biggest_delay'] = delayed_stops[0] if len(delayed_stops) else 0
        context['biggest_delay_time'] = int(delayed_stops[0].actual_departure_delay.seconds / 60) if len(delayed_stops) else 0
        context['average_delay'] = round(
            (sum([d.actual_departure_delay.seconds / 60 for d in delayed_stops]) / len(delayed_stops))) if delayed_stops else None
        return context
