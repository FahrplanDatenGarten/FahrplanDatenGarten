from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from . import views

app_name = 'netzkarte'
urlpatterns = [
    path(
        '',
        TemplateView.as_view(
            template_name="netzkarte/index.html"),
        name='index'),
    path('api', views.convert_toJson, name='api'),
    path('d3api', cache_page(60 * 120)(views.d3_tree), name='d3api'),
]
