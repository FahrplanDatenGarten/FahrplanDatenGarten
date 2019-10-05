
from django.urls import path
from . import views
urlpatterns = [
    path('', views.convert_toJson, name='index'),
]
