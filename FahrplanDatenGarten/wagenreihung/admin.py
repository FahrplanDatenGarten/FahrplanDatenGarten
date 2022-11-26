from django.contrib import admin

from .models import *


class CoachJourneyStopAdmin(admin.ModelAdmin):
    list_display = (
        'coach',
        'journeystop',
    )

admin.site.register(CoachJourneyStop, CoachJourneyStopAdmin)
admin.site.register([Coach])
