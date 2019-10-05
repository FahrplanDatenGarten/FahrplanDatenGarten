from django.views.generic import TemplateView
from django.urls import path
from . import views

urlpatterns = [
    path('api', views.convert_toJson, name='api'),
    path('', TemplateView.as_view(template_name="home.html"), name='index'),
]
