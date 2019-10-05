from django.shortcuts import render
from django.http import HttpResponse
import json
import datetime
from core import models


def get_demojson(request):
    fobj = open("../demo.json")
    demoJson=fobj.readlines()
    fobj.close()
    return HttpResponse(demoJson)

def convert_toJson(request):
	current_journeys = models.Journey.objects.filter(stop__journeystop__actual_departure_time__lte = datetime.datetime.now(),stop__journeystop__actual_arrival_time__gte = datetime.datetime.now())

	returnDict = {
		"current_journeys":  current_journeys.count(),
		#"journeys_delayed": current_journeys
		"biggest_delay": None




}

	return HttpResponse(json.dumps(returnDict))

 	
