from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'fgrfiller'
urlpatterns = [
    path(
        '',
        TemplateView.as_view(
            template_name="FGRFiller/form.html"),
        name='index'),
    path(
        'assistant/bookingnr/1',
        views.BookingNrAssistant1View.as_view(),
        name='bookingnr_assistant_1'),
    path(
        'pdf',
        views.GeneratePDFView.as_view(),
        name='pdf'),
]
