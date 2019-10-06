from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F
from django.views.generic import TemplateView
import json
from django.core.serializers.json import DjangoJSONEncoder
import datetime
from core import models


def get_demojson(request):
    fobj = open("../demo.json")
    demoJson=fobj.readlines()
    fobj.close()
    return JsonResponse(demoJson)

def convert_toJson(request):
	current_journeys = models.Journey.objects.filter(
		stop__journeystop__actual_departure_time__lte = datetime.datetime.now()).filter(
		stop__journeystop__actual_arrival_time__gte = datetime.datetime.now()
	).distinct()
	current_stops = models.JourneyStop.objects.filter(journey__in = current_journeys,actual_departure_time__lte = datetime.datetime.now()).order_by('actual_departure_time')
	delayed_stops = {}
	for stop in current_stops:
		delayed_stops[stop.journey]={
		        "name": stop.journey.name,
      			"plannedDepature": stop.planned_departure_time,
       		        "actualDepature": stop.actual_departure_time,
    			"delay": (stop.actual_departure_time-stop.planned_departure_time).total_seconds() / 60,
    			"date": stop.journey.date,
     			"id": stop.journey.journey_id,
     			"source": stop.journey.source.name,
     			"agency": stop.journey.agency.name
		}
	delayed_stops = list(sorted(delayed_stops.values(),key = lambda d : d['delay'],reverse=True))
	returnDict = {
		"current_journeys":  current_journeys.count(),
		"journeys_delayed": len({d['name'] for d in delayed_stops}),
		"biggest_delay": delayed_stops,
		"average_delay": (sum([d['delay'] for d in delayed_stops]) / len(delayed_stops)) if delayed_stops else None
	}

	return JsonResponse(returnDict,encoder=DjangoJSONEncoder)

class IndexView(TemplateView):
    template_name = 'templates/index.html'
