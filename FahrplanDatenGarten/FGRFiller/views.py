import datetime
import re

from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

import FGRFiller.utils
from core.models import Journey, JourneyStop


def create_pdf(request):
    now = datetime.datetime.now()
    trip_date = datetime.datetime.strptime(
        request.POST.get(
            'date',
            now.strftime('%Y-%m-%d')),
        '%Y-%m-%d')
    starttime = datetime.datetime.strptime(
        request.POST.get(
            'starttime',
            now.strftime('%H:%M')),
        '%H:%M')
    endtime = datetime.datetime.strptime(
        request.POST.get(
            'endtime',
            now.strftime('%H:%M')),
        '%H:%M')
    arrivaldate = datetime.datetime.strptime(request.POST.get(
        'arrivaldate', now.strftime('%Y-%m-%d')), '%Y-%m-%d')
    arrivaltime = datetime.datetime.strptime(
        request.POST.get(
            'arrivaltime',
            now.strftime('%H:%M')),
        '%H:%M')
    firsttraintime = datetime.datetime.strptime(
        request.POST.get(
            'firsttraintime',
            now.strftime('%H:%M')),
        '%H:%M')
    arrivaltraintype = re.search(
        '([A-Z])+',
        request.POST.get(
            'arrivaltrain',
            ''))
    arrivaltrainnum = re.search(
        '([0-9])+',
        request.POST.get(
            'arrivaltrain',
            ''))
    firsttraintype = re.search(
        '([A-Z])+',
        request.POST.get(
            'firsttrainid',
            ''))
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
    return FileResponse(
        FGRFiller.utils.generate_form(form_data),
        filename='fahrgastrechte.pdf')


class Assistant1View(View):
    template_name = 'FGRFiller/assistant1.html'

    def post(self, request, *args, **kwargs):
        try:
            trip_date = datetime.datetime.strptime(
                request.POST.get(
                    'date',
                    datetime.date.today().strftime('%Y-%m-%d')),
                '%Y-%m-%d').date()
        except ValueError:
            trip_date = datetime.date.today()
        journey = get_object_or_404(
            Journey,
            name="{} {}".format(
                self.request.POST['traintype'],
                self.request.POST['trainnum']),
            date=trip_date)
        return render(request, self.template_name, {'journey': journey})


class Assistant2View(View):
    template_name = 'FGRFiller/assistant2.html'

    def post(self, request, *args, **kwargs):
        journey = get_object_or_404(Journey, pk=request.POST.get('journey'))
        startstation = get_object_or_404(
            JourneyStop,
            journey=journey,
            stop__pk=request.POST.get('startstation'))
        endstation = get_object_or_404(
            JourneyStop,
            journey=journey,
            stop__pk=request.POST.get('endstation'))
        print(startstation.stop.stopname_set.first())

        form_data = {
            'S1F1': "{:02}".format(journey.date.day),
            'S1F2': "{:02}".format(journey.date.month),
            'S1F3': str(journey.date.year)[-2:],
            'S1F4': startstation.stop.stopname_set.first(),
            'S1F5': "{:02}".format(startstation.planned_departure_time.hour),
            'S1F6': "{:02}".format(startstation.planned_departure_time.minute),
            'S1F7': endstation.stop.stopname_set.first(),
            'S1F8': "{:02}".format(endstation.planned_arrival_time.hour),
            'S1F9': "{:02}".format(endstation.planned_arrival_time.minute),
            'S1F10': "{:02}".format(endstation.actual_arrival_time.day),
            'S1F11': "{:02}".format(endstation.actual_arrival_time.month),
            'S1F12': str(endstation.actual_arrival_time.year)[-2:],
            'S1F13': re.search('([A-Z])+', journey.name).group(0),
            'S1F14': re.search('([0-9])+', journey.name).group(0),
            'S1F15': "{:02}".format(endstation.actual_arrival_time.hour),
            'S1F16': "{:02}".format(endstation.actual_arrival_time.minute),
            'S1F17': re.search('([A-Z])+', journey.name).group(0),
            'S1F18': re.search('([0-9])+', journey.name).group(0),
            'S1F19': "{:02}".format(startstation.planned_departure_time.hour),
            'S1F20': "{:02}".format(startstation.planned_departure_time.minute),
        }
        print(re.search('([A-Z])+', journey.name).group(0))
        return FileResponse(
            FGRFiller.utils.generate_form(form_data),
            filename='fahrgastrechte.pdf')
