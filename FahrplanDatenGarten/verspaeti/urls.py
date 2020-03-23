from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from . import views

app_name = 'verspaeti'
urlpatterns = [
    path('', cache_page(60 * 30)(views.IndexView.as_view()), name='index'),
]
