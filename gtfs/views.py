from django.http import HttpResponse
from core import models
import csv,io
# Create your views here.

def agencyexport():
    output = io.StringIO()

    fieldnames = ['agency_id', 'agency_name', 'agency_url', 'agency_timezone']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for agency in models.Agency.objects.all():
        writer.writerow({'agency_id': agency.id, 'agency_name': agency.name, 'agency_url': '', 'agency_timezone': 'Europe/Berlin'})
    return output.getvalue()

def stopexport():
    output = io.StringIO()

    fieldnames = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    writer = csv.DictWriter(output, fieldnames=fieldnames)

    writer.writeheader()

    for stop in models.Stop.objects.all().prefetch_related("stopname_set","stoplocation_set"):
        stopname = stop.stopname_set.first()
        stoplocation = stop.stoplocation_set.first()
        if stoplocation:
            writer.writerow({'stop_id': stop.id, 'stop_name': stopname, 'stop_lat': stoplocation.latitude, 'stop_lon': stoplocation.longitude})
        else:
            writer.writerow({'stop_id': stop.id, 'stop_name': stopname})

    return output.getvalue()

def gtfsexport(request):

    return HttpResponse(stopexport(),content_type="text/plain")