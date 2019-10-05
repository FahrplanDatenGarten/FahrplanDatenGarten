from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import FGRFiller.utils
import datetime
import re

def create_pdf(request):
    trip_date = datetime.datetime.strptime(request.POST.get('date', ''), '%Y-%m-%d')
    starttime = datetime.datetime.strptime(request.POST.get('starttime', ''), '%H:%M')
    endtime = datetime.datetime.strptime(request.POST.get('endtime', ''), '%H:%M')
    arrivaldate = datetime.datetime.strptime(request.POST.get('arrivaldate', ''), '%Y-%m-%d')
    arrivaltime = datetime.datetime.strptime(request.POST.get('arrivaltime', ''), '%H:%M')
    firsttraintime = datetime.datetime.strptime(request.POST.get('firsttraintime', ''), '%H:%M')
    arrivaltraintype = re.search('([A-Z])+', request.POST.get('arrivaltrain', '')).group()
    arrivaltrainnum = re.search('([0-9])+', request.POST.get('arrivaltrain', '')).group()
    firsttraintype = re.search('([A-Z])+', request.POST.get('firsttrainid', '')).group()
    firsttrainnum = re.search('([0-9])+', request.POST.get('firsttrainid', '')).group()

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
