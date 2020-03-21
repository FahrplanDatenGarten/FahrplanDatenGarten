import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.views.generic import TemplateView
from plotly.graph_objs import Pie
from plotly.offline import plot

from core import models


def get_demojson(request):
    fobj = open("../demo.json")
    demoJson = fobj.readlines()
    fobj.close()
    return JsonResponse(demoJson)


def convert_toJson(request):
    current_journeys = models.Journey.objects.filter(
        stop__journeystop__actual_departure_time__lte=datetime.datetime.now()).filter(
        stop__journeystop__actual_arrival_time__gte=datetime.datetime.now()
    ).distinct()
    current_stops = models.JourneyStop.objects.filter(
        journey__in=current_journeys,
        actual_departure_time__lte=datetime.datetime.now()).order_by('actual_departure_time')
    delayed_stops = {}
    for stop in current_stops:
        if not stop.planned_departure_time or not stop.actual_departure_time:
            break
        delayed_stops[stop.journey] = {
            "name": stop.journey.name,
            "plannedDepature": stop.planned_departure_time,
            "actualDepature": stop.actual_departure_time,
            "delay": (stop.actual_departure_time - stop.planned_departure_time).total_seconds() / 60,
            "date": stop.journey.date,
            "id": stop.journey.journey_id,
            "source": stop.journey.source.name,
            "agency": stop.journey.agency.name
        }
    delayed_stops = list(x for x in sorted(delayed_stops.values(
    ), key=lambda d: d['delay'], reverse=True) if x['delay'] >= 5)
    returnDict = {
        "current_journeys": current_journeys.count(),
        "journeys_delayed": len({d['name'] for d in delayed_stops}),
        "biggest_delay": delayed_stops,
        "average_delay": (sum([d['delay'] for d in delayed_stops]) / len(delayed_stops)) if delayed_stops else None
    }

    return JsonResponse(returnDict, encoder=DjangoJSONEncoder)


class IndexView(TemplateView):
    template_name = "verspaeti/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_journeys = models.Journey.objects.filter(
            stop__journeystop__actual_departure_time__lte=datetime.datetime.now()).filter(
            stop__journeystop__actual_arrival_time__gte=datetime.datetime.now()).distinct()
        current_stops = models.JourneyStop.objects.filter(
            journey__in=current_journeys,
            actual_departure_time__lte=datetime.datetime.now()).order_by('actual_departure_time')

        delayed_stops = {}
        for stop in current_stops:
            if not stop.planned_departure_time or not stop.actual_departure_time:
                break
            delayed_stops[stop.journey] = {
                "name": stop.journey.name,
                "plannedDepature": stop.planned_departure_time,
                "actualDepature": stop.actual_departure_time,
                "delay": int((stop.actual_departure_time - stop.planned_departure_time).total_seconds() / 60),
                "date": stop.journey.date,
                "id": stop.journey.journey_id,
                "source": stop.journey.source.name,
                "agency": stop.journey.agency.name
            }

        delayed_stops = list(x for x in sorted(delayed_stops.values(
        ), key=lambda d: d['delay'], reverse=True) if x['delay'] >= 5)
        num_delayed_stops = len({d['name'] for d in delayed_stops})

        colors = ['red', 'limegreen']
        labels = ['Pünktlich', 'Zu spät']
        values = [
            current_journeys.count() -
            num_delayed_stops,
            num_delayed_stops]
        plot_div = plot([Pie(labels=labels, values=values,
                             marker=dict(colors=colors))], output_type='div')

        context['plot_div'] = plot_div
        context['delayed_stops'] = delayed_stops
        context['current_journeys'] = current_journeys.count()
        context['journeys_delayed'] = len({d['name'] for d in delayed_stops}),
        context['biggest_delay'] = delayed_stops[0] if len(
            delayed_stops) else 0
        context['average_delay'] = round(
            (sum([d['delay'] for d in delayed_stops]) / len(delayed_stops))) if delayed_stops else None
        return context
