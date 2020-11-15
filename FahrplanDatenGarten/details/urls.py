from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'details'
urlpatterns = [
    path(
        'traindetails/<str:train_name>/page<int:page_num>',
        cache_page(60*5)(views.TrainDetailsByNameView.as_view()),
        name='traindetailsbyname'),
    path(
        'traindetails/search',
        cache_page(60*5)(views.TrainDetailsByNameSearchView.as_view()),
        name='traindetailsbynamesearch'),
    path(
        'traindetails/api/details/<int:journey_id>',
        cache_page(60 * 30)(views.JourneyDetailsAPI.as_view()),
        name='traindetailsapidetails'),
    path(
        'traindetails/api/delay_graph',
        cache_page(60 * 60 * 7)(views.GenerateDelayJourneyGraph.as_view()),
        name='delaygraph'),
    path(
        'traindetails/api/long_term_delay_graph/<str:train_name>',
        cache_page(60 * 60 * 24)(views.GenerateLongTermDelayGraph.as_view()),
        name='longtermdelaygraph'),
    path(
        'traindetails/api/long_term_delay_graph/<str:train_name>/<int:days>',
        cache_page(60 * 60 * 24)(views.GenerateLongTermDelayGraph.as_view()),
        name='longtermdelaygraph'),
]
