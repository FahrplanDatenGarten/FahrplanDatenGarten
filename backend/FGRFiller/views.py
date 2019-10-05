from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import FGRFiller.utils

def create_pdf(request):
    form_data = {
        'S1F1': request.POST.get('date', ''),
        'S1F4': request.POST.get('startstation', ''),
        'S1F5': request.POST.get('starttime', ''),
        'S1F7': request.POST.get('endstation', ''),
        'S1F8': request.POST.get('endtime', ''),
        'S1F10': request.POST.get('arrivaldate', ''),
        'S1F14': request.POST.get('arrivaltrain', ''),
        'S1F15': request.POST.get('arrivaltime', ''),
        'S1F17': request.POST.get('firsttrainid', ''),
        'S1F19': request.POST.get('firsttraintime', ''),
        }
    return FileResponse(FGRFiller.utils.generate_form(form_data), filename='fahrgastrechte.pdf')
