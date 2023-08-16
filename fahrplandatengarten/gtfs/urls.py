from django.urls import path

from . import views

app_name = 'gtfs'
urlpatterns = [
    path('gtfs', views.gtfsexport, name='gtfs')
]
