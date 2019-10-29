from django.contrib import admin

# Register your models here.
from .models import Stop, StopID, StopIDKind, StopName, StopLocation, Source, Agency, Journey, JourneyStop

admin.site.register([Stop, StopID, StopIDKind, StopName, StopLocation, Source, Agency, Journey, JourneyStop])
