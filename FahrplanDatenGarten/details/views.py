import datetime
from io import BytesIO
from typing import List

import numpy as np
from django import urls
from django.core.exceptions import ObjectDoesNotExist
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Page, Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.http import FileResponse, JsonResponse, HttpResponseNotFound
from django.views import View
from django.views.generic import TemplateView
from matplotlib import pyplot
from scipy import interpolate

from core.models import Journey, JourneyStop


class JourneyDetailsAPI(View):
    def get(self, request: WSGIRequest, journey_id: int, *args, **kwargs):
        try:
            journey = Journey.objects.get(pk=journey_id)
        except ObjectDoesNotExist:
            return HttpResponseNotFound("404 - Train not found")
        journeystops = JourneyStop.objects.filter(
            journey=journey
        ).order_by('planned_departure_time')
        stops = [{
            "name": journeystop.stop.name,
            "planned_time": journeystop.earlier_time().strftime("%H:%M") if journeystop.earlier_time() is not None else None,
            "actual_delay_mins": journeystop.get_delay().total_seconds() / 60 if journeystop.get_delay() is not None else None,
            "actual_time": journeystop.actual_earlier_time().strftime("%H:%M") if journeystop.actual_earlier_time() is not None else None,
            "cancelled": journeystop.cancelled
        } for journeystop in journeystops]
        response_dict = {
            "date": journey.date,
            "stops": stops
        }
        return JsonResponse(response_dict)


class GenerateDelayJourneyGraph(View):
    def get(self, request: WSGIRequest, *args, **kwargs):
        labels = [delay_per_date_raw.split(
            ',')[0] for delay_per_date_raw in request.GET.getlist('delays_per_date')]
        labels.reverse()
        group1_means = [float(delay_per_date_raw.split(',')[1])
                        for delay_per_date_raw in request.GET.getlist('delays_per_date')]
        group1_means.reverse()

        plot_figure, plot_axes = pyplot.subplots()
        plot_figure.subplots_adjust(bottom=0.18, top=0.95)
        x_pos = [i for i, _ in enumerate(labels)]

        pyplot.bar(x_pos, group1_means, label='Group 1')
        pyplot.xticks(x_pos, labels, rotation=45)
        pyplot.ylabel('Verspätung in Minuten')
        plot_temporary_file = BytesIO()
        pyplot.savefig(plot_temporary_file, format='png')
        plot_temporary_file.seek(0)
        return FileResponse(plot_temporary_file, filename="delays.png")


class GenerateLongTermDelayGraph(View):
    def get_journey_delays(self, train_name: str, days: int):
        journeys = Journey.objects.filter(
            name=train_name,
            date__gte=datetime.date.today() - datetime.timedelta(days=days)
        )
        return_delays: np.ndarray = np.array([])
        return_labels: np.ndarray = np.array([])
        for journey in journeys:
            if journey.cancelled:
                continue
            journeystops = JourneyStop.objects.filter(
                journey=journey
            )
            if len(journeystops) != 0:
                delays: List[float] = [float((journeystop.get_delay() if journeystop.get_delay(
                ) is not None else datetime.timedelta()).total_seconds()) / 60 for journeystop in journeystops]
                return_delays = np.append(
                    return_delays, [
                        sum(delays) / len(journeystops)])
                return_labels = np.append(
                    return_labels, [
                        (journey.date - datetime.date.today()).days])
        return {
            "delays": return_delays,
            "labels": return_labels
        }

    def get(self, request: WSGIRequest, train_name: str, days: int = 90, *args, **kwargs):
        journeys_data = self.get_journey_delays(train_name, days)
        labels: np.ndarray = journeys_data['labels']
        delay_data: np.ndarray = journeys_data['delays']
        labels_argsort = np.argsort(labels)
        labels = labels[labels_argsort]
        delay_data = delay_data[labels_argsort]
        xnew = np.linspace(labels.min(initial=-days), labels.max(initial=-days), 500)

        interpolate_function = interpolate.interp1d(
            labels, delay_data, kind='linear')
        ynew = interpolate_function(xnew)

        plot_figure, plot_axes = pyplot.subplots()
        plot_figure.subplots_adjust(bottom=0.18, top=0.95)

        pyplot.plot(xnew, ynew)
        pyplot.xlabel(
            f"Tage seit dem {datetime.date.today().strftime('%d.%m.%Y')}")
        pyplot.ylabel('Verspätung in Minuten')
        plot_temporary_file = BytesIO()
        pyplot.savefig(plot_temporary_file, format='png')
        plot_temporary_file.seek(0)
        return FileResponse(plot_temporary_file, filename="delays.png")


class TrainDetailsByNameView(TemplateView):
    template_name = "details/traindetailsbyname.html"

    @staticmethod
    def get_journeys_data(journey_paginator_page: Page) -> List[dict]:
        return_journeys_data: List[dict] = []
        for journey in journey_paginator_page:
            journeystops = JourneyStop.objects.filter(
                journey=journey
            )
            delays: List[datetime.timedelta] = [journeystop.get_delay() if journeystop.get_delay(
            ) is not None else datetime.timedelta() for journeystop in journeystops]
            average_delay = sum(
                delays, datetime.timedelta()) / len(journeystops)
            return_journeys_data.append({
                "id": journey.id,
                "date": journey.date,
                "cancelled": journey.cancelled,
                "average_delay": round(average_delay.total_seconds() / 60, 1),
                "maximum_delay": round(max(delays).total_seconds() / 60)
            })
        return return_journeys_data

    def get_context_data(self, train_name: str, page_num: int, **kwargs):
        context = super().get_context_data(**kwargs)
        db_journeys = Journey.objects.filter(
            name=train_name
        ).order_by('-date')
        if len(db_journeys) != 0:
            journey_paginator = Paginator(db_journeys, 9)
            journey_paginator_page = journey_paginator.get_page(page_num)
            journeys_data = self.get_journeys_data(journey_paginator_page)
            delay_graph_query_parameters = "&".join(
                [f"delays_per_date={journey_data['date']},{journey_data['average_delay']}" for
                 journey_data in journeys_data])
            context['train_name'] = train_name
            context['trip'] = {
                "from": db_journeys.first().journeystop_set.order_by('planned_departure_time').first().stop.name,
                "to": db_journeys.first().journeystop_set.filter(
                    planned_arrival_time__isnull=False
                ).order_by('planned_arrival_time').last().stop.name}
            context['journeys'] = journeys_data
            context['delay_graph_url'] = f"{urls.reverse('details:delaygraph')}?{delay_graph_query_parameters}"
            context['long_term_delay_graph_url'] = f"{urls.reverse('details:longtermdelaygraph', kwargs={'train_name': train_name})}"
        else:
            context['error_message'] = "404 - Train not found"
        return context
