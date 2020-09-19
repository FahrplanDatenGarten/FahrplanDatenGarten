import datetime
import random

import requests
from django.http import FileResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View
from lxml import etree

import FGRFiller.utils
from FGRFiller.forms.assistant_order_number import FGRFillerAsstiantOrderNumberForm
from FGRFiller.forms.data import FGRFillerDataForm
from FGRFiller.utils import FillFormFieldsBahnCard100SeasonTicket, FillFormFieldsCompensation
from core.models import JourneyStop


class StartView(View):
    template_name = "FGRFiller/start.html"

    def get(self, request):
        assistant_order_number_form = FGRFillerAsstiantOrderNumberForm()
        return render(request, self.template_name, {
            "assistant_order_number_form": assistant_order_number_form
        })


class BookingNrAssistant1View(View):
    template_name = 'FGRFiller/check_data.html'

    def post(self, request, *args, **kwargs):
        assistant_form = FGRFillerAsstiantOrderNumberForm(request.POST)
        if assistant_form.is_valid():
            xml = '<rqorder on="{}"/><authname tln="{}"/>'.format(
                assistant_form.cleaned_data['order_number'], assistant_form.cleaned_data['last_name'])
            url = 'https://fahrkarten.bahn.de/mobile/dbc/xs.go'
            tnr = random.getrandbits(64)
            ts = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            request_body = '<rqorderdetails version="2.0"><rqheader tnr="{0}" ts="{1}" v="19100000" d="iPhone10,4" os="iOS_13.1.3" app="NAVIGATOR"/>{2}</rqorderdetails>'.format(
                tnr,
                ts,
                xml)
            response = requests.post(url, data=request_body).content
            parsed_response = etree.fromstring(response)
            if parsed_response.tag != "rperror":
                trainlist = parsed_response.find('order').find(
                    'schedulelist').find('out').find('trainlist')

                arrival_planned_time = datetime.time.fromisoformat(
                    trainlist[-1].find('arr').attrib['t'])

                first_delayed_train = None

                for train in trainlist:
                    train_arrival_planned_time = datetime.time.fromisoformat(
                        train.find('arr').attrib['t'])
                    try:
                        if JourneyStop.objects.filter(
                                journey__name=train.find('gat').text + " " + train.find('zugnr').text,
                                stop__stopid__name=train.find('arr').find('nr').text,
                                stop__stopid__kind__name="eva",
                                planned_arrival_time=timezone.make_aware(datetime.datetime.fromisoformat(
                                    train.find('arr').attrib['dt']).replace(
                                    hour=train_arrival_planned_time.hour,
                                    minute=train_arrival_planned_time.minute)),
                        ).first().actual_arrival_delay >= datetime.timedelta(minutes=5):
                            first_delayed_train = train
                            break
                    except AttributeError:
                        continue

                try:
                    arrival_actual_datetime = JourneyStop.objects.filter(
                        journey__name=trainlist[-1].find('gat').text + " " + trainlist[-1].find('zugnr').text,
                        stop__stopid__name=trainlist[-1].find('arr').find('nr').text,
                        stop__stopid__kind__name="eva",
                        planned_arrival_time=timezone.make_aware(datetime.datetime.fromisoformat(trainlist[-1].find('arr').attrib['dt']).replace(
                            hour=arrival_planned_time.hour,
                            minute=arrival_planned_time.minute)),
                    ).first().get_actual_arrival_time()
                except AttributeError:
                    arrival_actual_datetime = None
                    pass

                form = FGRFillerDataForm({
                    "travel_date": datetime.datetime.fromisoformat(parsed_response.find('order').attrib['sdt']).date().strftime(
                        '%Y-%m-%d'),
                    "departure_stop_name": trainlist[0].find('dep').find('n').text,
                    "departure_planned_time": datetime.time.fromisoformat(trainlist[0].find('dep').attrib['t']).strftime(
                        "%H:%M"),
                    "arrival_stop_name": trainlist[-1].find('arr').find('n').text,
                    "arrival_planned_time": arrival_planned_time.strftime("%H:%M"),
                    "arrival_actual_date": timezone.localdate(arrival_actual_datetime).strftime('%Y-%m-%d') if arrival_actual_datetime is not None else "",
                    "arrival_actual_time": timezone.localtime(arrival_actual_datetime).strftime('%H:%M') if arrival_actual_datetime is not None else "",
                    "arrival_actual_product_type": trainlist[-1].find('gat').text,
                    "arrival_actual_product_number": trainlist[-1].find('zugnr').text,
                    "first_name": parsed_response.find('order').find('tcklist')[0].find('mtk').find('reisender_vorname').text,
                    "last_name": parsed_response.find('order').find('tcklist')[0].find('mtk').find('reisender_nachname').text,
                    "first_delayed_train_product_type": first_delayed_train.find('gat').text if first_delayed_train is not None else "",
                    "first_delayed_train_product_number": first_delayed_train.find('zugnr').text if first_delayed_train is not None else "",
                    "first_delayed_train_departure_planned": datetime.time.fromisoformat(
                        first_delayed_train.find('dep').attrib['t']).strftime("%H:%M") if first_delayed_train is not None else "",
                    "changed_train": len(trainlist) > 1,
                    "changed_train_last_station": trainlist[-1].find('dep').find('n').text,
                })

                return render(request, self.template_name, {
                    "form": form
                })
            else:
                return render(request, "FGRFiller/start.html", {
                    "assistant_order_number_form": assistant_form,
                    "assistant_order_number_form_error": parsed_response.find('error').find('txt').text
                })
        else:
            return render(request, "FGRFiller/start.html", {
                "assistant_order_number_form": assistant_form
            })


class ManualFormView(View):
    def get(self, request):
        form = FGRFillerDataForm()
        return render(request, "FGRFiller/check_data.html", {
            "form": form
        })


class GeneratePDFView(View):
    def post(self, request, *args, **kwargs):
        form = FGRFillerDataForm(request.POST)
        if form.is_valid():
            form_fields = FGRFiller.utils.fill_form_fields(
                travel_date=form.cleaned_data['travel_date'],
                departure_stop_name=form.cleaned_data['departure_stop_name'],
                departure_planned_time=form.cleaned_data['departure_planned_time'],
                arrival_stop_name=form.cleaned_data['arrival_stop_name'],
                arrival_planned_time=form.cleaned_data['arrival_planned_time'],
                arrival_actual_datetime=datetime.datetime.combine(
                    form.cleaned_data['arrival_actual_date'],
                    form.cleaned_data['arrival_actual_time']),
                arrival_actual_product_type=form.cleaned_data['arrival_actual_product_type'],
                arrival_actual_product_number=form.cleaned_data['arrival_actual_product_number'],
                first_delayed_train_product_type=form.cleaned_data['first_delayed_train_product_type'],
                first_delayed_train_product_number=form.cleaned_data['first_delayed_train_product_number'],
                first_delayed_train_departure_planned=form.cleaned_data['first_delayed_train_departure_planned'],
                connecting_train_missed=form.cleaned_data['connecting_train_missed'],
                connecting_train_missed_station=form.cleaned_data['connecting_train_missed_station'],
                changed_train=form.cleaned_data['changed_train'],
                changed_train_last_station=form.cleaned_data['changed_train_last_station'],
                journey_not_start_or_cut_short=form.cleaned_data['journey_not_start_or_cut_short'],
                journey_not_start_or_cut_short_station=form.cleaned_data['journey_not_start_or_cut_short_station'],
                journey_cut_short_additional_costs=form.cleaned_data['journey_cut_short_additional_costs'],
                journey_cut_short_additional_costs_station=form.cleaned_data[
                    'journey_cut_short_additional_costs_station'],
                compensation=form.cleaned_data['compensation'] if isinstance(
                    form.cleaned_data['compensation'],
                    FillFormFieldsCompensation) else FillFormFieldsCompensation[
                    form.cleaned_data['compensation'].split('.')[1]] if form.cleaned_data[
                                                                            'compensation'] != '' else None,
                academic_title=form.cleaned_data['academic_title'],
                company=form.cleaned_data['company'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                address_c_o_extra_details=form.cleaned_data['address_c_o_extra_details'],
                telephone_number=form.cleaned_data['telephone_number'],
                address_street=form.cleaned_data['address_street'],
                address_house_nr=form.cleaned_data['address_house_nr'],
                address_postal_code=form.cleaned_data['address_postal_code'],
                address_city=form.cleaned_data['address_city'],
                address_country=form.cleaned_data['address_country'],
                bahncard_100_season_ticket=form.cleaned_data['bahncard_100_season_ticket'] if isinstance(
                    form.cleaned_data['bahncard_100_season_ticket'],
                    FillFormFieldsBahnCard100SeasonTicket) else FillFormFieldsBahnCard100SeasonTicket[
                    form.cleaned_data['bahncard_100_season_ticket'].split('.')[1]] if form.cleaned_data[
                                                                                          'bahncard_100_season_ticket'] != '' else None,
                bahncard_100_season_ticket_number=form.cleaned_data['bahncard_100_season_ticket_number'],
                date_of_birth=form.cleaned_data['date_of_birth'])
            return FileResponse(
                FGRFiller.utils.generate_form(form_fields),
                filename='fahrgastrechte.pdf')
        else:
            return render(request, "FGRFiller/check_data.html", {
                "form": form
            })
