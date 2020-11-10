from django.urls import path

from . import views

app_name = 'details'
urlpatterns = [
    path(
        'traindetails/<str:train_name>/page<int:page_num>',
        views.TrainDetailsByNameView.as_view(),
        name='traindetailsbyname'),
    path(
        'traindetails/api/delay_graph',
        views.GenerateDelayJourneyGraph.as_view(),
        name='delaygraph'),
    path(
        'traindetails/api/long_term_delay_graph/<str:train_name>',
        views.GenerateLongTermDelayGraph.as_view(),
        name='longtermdelaygraph'),
    path(
        'traindetails/api/long_term_delay_graph/<str:train_name>/<int:days>',
        views.GenerateLongTermDelayGraph.as_view(),
        name='longtermdelaygraph'),
]
