from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View
from core.models import Journey, JourneyStop
import FGRFiller.utils
import datetime
import json
import re

def create_pdf(request):
    now = datetime.datetime.now()
    trip_date = datetime.datetime.strptime(request.POST.get('date', now.strftime('%Y-%m-%d')), '%Y-%m-%d')
    starttime = datetime.datetime.strptime(request.POST.get('starttime', now.strftime('%H:%M')), '%H:%M')
    endtime = datetime.datetime.strptime(request.POST.get('endtime', now.strftime('%H:%M')), '%H:%M')
    arrivaldate = datetime.datetime.strptime(request.POST.get('arrivaldate', now.strftime('%Y-%m-%d')), '%Y-%m-%d')
    arrivaltime = datetime.datetime.strptime(request.POST.get('arrivaltime', now.strftime('%H:%M')), '%H:%M')
    firsttraintime = datetime.datetime.strptime(request.POST.get('firsttraintime', now.strftime('%H:%M')), '%H:%M')
    arrivaltraintype = re.search('([A-Z])+', request.POST.get('arrivaltrain', ''))
    arrivaltrainnum = re.search('([0-9])+', request.POST.get('arrivaltrain', ''))
    firsttraintype = re.search('([A-Z])+', request.POST.get('firsttrainid', ''))
    firsttrainnum = re.search('([0-9])+', request.POST.get('firsttrainid', ''))

    form_data = {
        'S1F1': "{:02}".format(trip_date.day),
        'S1F2': "{:02}".format(trip_date.month),
        'S1F3': str(trip_date.year)[-2:],
        'S1F4': request.POST.get('startstation', ''),
        'S1F5': "{:02}".format(starttime.hour),
        'S1F6': "{:02}".format(starttime.minute),
        'S1F7': request.POST.get('endstation', ''),
        'S1F8': "{:02}".format(endtime.hour),
        'S1F9': "{:02}".format(endtime.minute),
        'S1F10': "{:02}".format(arrivaldate.day),
        'S1F11': "{:02}".format(arrivaldate.month),
        'S1F12': str(arrivaldate.year)[-2:],
        'S1F13': arrivaltraintype,
        'S1F14': arrivaltrainnum,
        'S1F15': "{:02}".format(arrivaltime.hour),
        'S1F16': "{:02}".format(arrivaltime.minute),
        'S1F17': firsttraintype,
        'S1F18': firsttrainnum,
        'S1F19': "{:02}".format(firsttraintime.hour),
        'S1F20': "{:02}".format(firsttraintime.minute),
        }
    return FileResponse(FGRFiller.utils.generate_form(form_data), filename='fahrgastrechte.pdf')

class AssistantStationChooseView(View):
    template_name = 'FGRFiller/assistant_choose_station.html'

    def post(self, request, *args, **kwargs):
        try:
            trip_date = datetime.datetime.strptime(request.POST.get('date', datetime.date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        except ValueError:
            trip_date = datetime.date.today()
        journey = get_object_or_404(Journey, name="{} {}".format(self.request.POST['traintype'], self.request.POST['trainnum']), date=trip_date)
        return render(request, self.template_name, {'journey': journey})

class AssistantMultihoopView(View):
    template_name = 'FGRFiller/assistant_multihop.html'

    def post(self, request, *args, **kwargs):
        journeys = []
        trains_available = []
        endstations_available = []
        select_station = False

        if request.POST.get('journey_json') is None:
            journey = get_object_or_404(Journey, pk=request.POST.get('journey'))
            startstation = get_object_or_404(JourneyStop, journey=journey, stop__pk=request.POST.get('startstation'))
            endstation = get_object_or_404(JourneyStop, journey=journey, stop__pk=request.POST.get('endstation'))
            journeys.append({
                'journey':journey,
                'start':startstation,
                'end':endstation
            })
            trains_available = endstation.stop.journey_set.filter(agency__name='db').all()
        else:
            # Parse the PrimaryKeys of the objects in a json string to journeys
            journeys = parse_journey_json(request.POST.get('journey_json'))
            if not request.GET.get('back') is None and len(journeys) > 1:
                journeys.pop(-1)
                trains_available = journeys[-1]['end'].stop.journey_set.filter(agency__name='db').all()
            else:
                if request.POST.get('endstation') is None:
                    select_station = True
                    journey = get_object_or_404(Journey, pk=request.POST.get('newtrain'))
                    print(journeys)
                    startstation = journeys[-1]['end']
                    # TODO: Also exclude stations before startstation
                    endstations_available = journey.stop.exclude(journeystop__pk=startstation.pk).all()
                    journeys.append({
                        'journey':journey,
                        'start':startstation,
                        'end':None
                    })
                else:
                    journeys[-1]['end'] = get_object_or_404(JourneyStop, journey=journeys[-1]['journey'], stop__pk=request.POST.get('endstation'))
                    # TODO: Exclude journeys that end here
                    trains_available = journeys[-1]['end'].stop.journey_set.filter(agency__name='db').all()

        # Store the PrimaryKeys of the objects in journeys in a json string
        journey_pks = []
        for journey_dict in journeys:
            obj_pks = {}
            for key, obj in journey_dict.items():
                if not obj is None:
                    obj_pks[key] = obj.pk
                else:
                    obj_pks[key] = None
            journey_pks.append(obj_pks)
        journey_json = json.dumps(journey_pks)

        return render(request, self.template_name, {
            'journey_json': journey_json,
            'journeys':journeys,
            'select_station':select_station,
            'availableTrains':trains_available,
            'availableEndstations':endstations_available
        })

class AssistantPdfView(View):
    def post(self, request, *args, **kwargs):
        if request.POST.get('journey_json') is None:
            firstjourney = get_object_or_404(Journey, pk=request.POST.get('journey'))
            firststation = get_object_or_404(JourneyStop, journey=firstjourney, stop__pk=request.POST.get('startstation'))
            laststation = get_object_or_404(JourneyStop, journey=firstjourney, stop__pk=request.POST.get('endstation'))

            lastjourney = firstjourney
            firstdelayedjourney = firstjourney
            firstdelayedstation = firststation
        else:
            journeys = parse_journey_json(request.POST.get('journey_json'))
            if journeys[-1]['end'] is None:
                journeys.pop(-1)

            firstjourney = journeys[0]['journey']
            firststation = journeys[0]['start']
            lastjourney = journeys[-1]['journey']
            laststation = journeys[-1]['end']
            # TODO: Find firstdelayedstation
            firstdelayedstation = journeys[0]['start']
            firstdelayedjourney = firstdelayedstation.journey

        form_data = {
            'S1F1': "{:02}".format(firstjourney.date.day),
            'S1F2': "{:02}".format(firstjourney.date.month),
            'S1F3': str(firstjourney.date.year)[-2:],
            'S1F4': firststation.stop.stopname_set.first(),
            'S1F5': "{:02}".format(firststation.planned_departure_time.hour),
            'S1F6': "{:02}".format(firststation.planned_departure_time.minute),
            'S1F7': laststation.stop.stopname_set.first(),
            'S1F8': "{:02}".format(laststation.planned_arrival_time.hour),
            'S1F9': "{:02}".format(laststation.planned_arrival_time.minute),
            'S1F10': "{:02}".format(alternative_date(laststation.actual_arrival_time, laststation.planned_arrival_time).day),
            'S1F11': "{:02}".format(alternative_date(laststation.actual_arrival_time, laststation.planned_arrival_time).month),
            'S1F12': str(alternative_date(laststation.actual_arrival_time, laststation.planned_arrival_time).year)[-2:],
            'S1F13': re.search('([A-Z])+', lastjourney.name).group(0),
            'S1F14': re.search('([0-9])+', lastjourney.name).group(0),
            'S1F15': "{:02}".format(alternative_date(laststation.actual_arrival_time, laststation.planned_arrival_time).hour),
            'S1F16': "{:02}".format(alternative_date(laststation.actual_arrival_time, laststation.planned_arrival_time).minute),
            'S1F17': re.search('([A-Z])+', firstdelayedjourney.name).group(0),
            'S1F18': re.search('([0-9])+', firstdelayedjourney.name).group(0),
            'S1F19': "{:02}".format(firstdelayedstation.planned_departure_time.hour),
            'S1F20': "{:02}".format(firstdelayedstation.planned_departure_time.minute),
            }
        return FileResponse(FGRFiller.utils.generate_form(form_data), filename='fahrgastrechte.pdf')

def alternative_date(primary, alternative):
    if not (primary is None):
        return primary
    else:
        return alternative

def parse_journey_json(journey_json):
    journeys = []
    for journey_dict in json.loads(journey_json):
        journey = get_object_or_404(Journey, pk=journey_dict['journey'])
        startstation = JourneyStop.objects.filter(pk=journey_dict['start']).first()
        endstation = JourneyStop.objects.filter(pk=journey_dict['end']).first()
        journeys.append({
            'journey':journey,
            'start':startstation,
            'end':endstation
        })
    return journeys
