"""fahrplandatengarten URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView

handler404 = 'fahrplandatengarten.core.views.page_not_found_view'

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('verspaeti:index'))),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    path('verspaeti/', include('fahrplandatengarten.verspaeti.urls', namespace='verspaeti')),
    path('fgr/', include('fahrplandatengarten.FGRFiller.urls', namespace='fgrfiller')),
    path('gtfs/', include('fahrplandatengarten.gtfs.urls', namespace='gtfs')),
    path('netzkarte/', include('fahrplandatengarten.netzkarte.urls', namespace='netzkarte')),
    path('details/', include('fahrplandatengarten.details.urls', namespace='details')),
]
