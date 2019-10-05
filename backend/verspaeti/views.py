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


	returnDict = {
		"current_journeys":  models.Journey.objects.filter(stop__journeystop__actual_departure_time__lte = datetime.datetime.now(),stop__journeystop__actual_arrival_time__gte = datetime.datetime.now()).count(),

		
		                  
		#"journeys_delayed": ANZAHL DER VERSPÄTETEN ZÜGE
		"biggest_delay": None




}

	return HttpResponse(json.dumps(returnDict))

 	
