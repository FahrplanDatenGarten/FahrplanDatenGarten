from django.views.generic import TemplateView
from django.urls import path
from . import views

app_name = 'verspaeti'
urlpatterns = [
    path('api', views.convert_toJson, name='api'),
    path('', views.IndexView.as_view(), name='index'),
]
