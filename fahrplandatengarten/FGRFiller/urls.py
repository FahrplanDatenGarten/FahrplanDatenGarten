from django.urls import path

from . import views

app_name = 'fgrfiller'
urlpatterns = [
    path(
        '',
        views.StartView.as_view(),
        name='index'),
    path(
        'assistant/bookingnr/1',
        views.BookingNrAssistant1View.as_view(),
        name='bookingnr_assistant_1'),
    path(
        'manual',
        views.ManualFormView.as_view(),
        name='manual'),
    path(
        'pdf',
        views.GeneratePDFView.as_view(),
        name='pdf'),
]
