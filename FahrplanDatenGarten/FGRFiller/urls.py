from django.views.generic import TemplateView
from django.urls import path
from . import views


app_name = 'fgrfiller'
urlpatterns = [
    path('', TemplateView.as_view(template_name="FGRFiller/form.html"), name='index'),
    path('assistant', views.AssistantStationChooseView.as_view(), name='assistant_choose_station'),
    path('assistant_multihop', views.AssistantMultihoopView.as_view(), name='assistant_multihop'),
    path('assistant_pdf', views.AssistantPdfView.as_view(), name='assistant_pdf'),
    path('pdf', views.create_pdf, name='pdf'),
]
