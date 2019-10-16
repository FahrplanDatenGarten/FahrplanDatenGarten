from django.views.generic import TemplateView
from django.urls import path
from . import views


app_name = 'fgrfiller'
urlpatterns = [
    path('', TemplateView.as_view(template_name="FGRFiller/form.html"), name='index'),
    path('assistant', views.Assistant1View.as_view(), name='assistant_1'),
    path('assistant', views.Assistant2View.as_view(), name='assistant_2'),
    path('pdf', views.create_pdf, name='pdf'),
]
