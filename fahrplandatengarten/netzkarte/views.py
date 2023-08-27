from fahrplandatengarten.core.models import Stop
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import JsonResponse

from . import STOPS
from .models import Connection


def convert_toJson(request):
    returnDict = {
        'connections': {}
    }

    for stop_id in STOPS:
        stop = Stop.objects.get(
            stopid__external_id=stop_id,
            stopid__kind__name='eva',
            stopid__kind__provider__internal_name='db'
        )
        returnDict['connections'][stop_id] = {
            'stationID': stop_id,
            'stationName': stop.name,
            'duration': {c.stop.get(
                ~Q(id=stop.pk)).stopid_set.first().external_id: c.duration.total_seconds() for c in stop.connection_set.all()},
            'lat': stop.latitude if stop.latitude is not None else 0,
            'lon': stop.longitude if stop.longitude is not None else 0,
        }

    returnDict['lines'] = {'nodes': [], 'links': []}
    for _, value in returnDict['connections'].items():
        returnDict['lines']['nodes'].append(
            {'id': value['stationName'], 'group': 1})
        for stop_id, duration in value['duration'].items():
            returnDict['lines']['links'].append(
                {
                    'source': [
                        value['lat'],
                        value['lon']],
                    'target': [
                        returnDict['connections'][stop_id]['lat'],
                        returnDict['connections'][stop_id]['lon']],
                    'duration': duration})

    return JsonResponse(returnDict, encoder=DjangoJSONEncoder)


def d3_tree(request):
    returnDict = {
        'stations': [],
        'connections': []
    }

    for stop_id in STOPS:
        stop = Stop.objects.get(
            stopid__external_id=stop_id,
            stopid__kind__name='eva',
            stopid__kind__provider__internal_name='db'
        )
        loc = [
            stop.longitude if stop.longitude is not None else 0,
            stop.latitude if stop.latitude is not None else 0,
        ]

        returnDict['stations'].append({
            'name': stop.name,
            'location': loc}
        )

        for next_stop_id in STOPS:
            if next_stop_id == stop_id:
                continue

            next_stop = Stop.objects.get(
                stopid__external_id=next_stop_id,
                stopid__kind__name='eva',
                stopid__kind__provider__internal_name='db'
            )
            next_loc = [
                next_stop.longitude if next_stop.longitude is not None else 0,
                next_stop.latitude if next_stop.latitude is not None else 0,
            ]

            duration = Connection.objects.filter(
                stop=stop).filter(
                stop=next_stop).first().duration.total_seconds() if Connection.objects.filter(
                stop=stop).filter(
                stop=next_stop).count() else 0

            returnDict['connections'].append({
                'link': [
                    loc,
                    next_loc
                ],
                'duration': duration
            })

    return JsonResponse(returnDict, encoder=DjangoJSONEncoder)
