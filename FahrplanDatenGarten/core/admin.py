from django.contrib import admin

# Register your models here.
from .models import (Journey, JourneyStop, Provider, Source, Stop, StopID,
                     StopIDKind)


class StopIDAdminInline(admin.TabularInline):
    model = StopID


class StopAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'primary_stop_id')
    inlines = [StopIDAdminInline]

    @staticmethod
    def primary_stop_id(obj):
        return obj.stopid_set.first().external_id


class JourneystopAdminInline(admin.TabularInline):
    model = JourneyStop
    fields = (
        'stop',
        'planned_arrival_time',
        'planned_departure_time',
        'actual_arrival_delay',
        'actual_departure_delay')


class JourneyAdmin(admin.ModelAdmin):
    inlines = (JourneystopAdminInline,)
    list_display = (
        'name',
        'date',
        'cancelled',
        'source',
    )


admin.site.register(Stop, StopAdmin)
admin.site.register(Journey, JourneyAdmin)
admin.site.register([StopID, StopIDKind, Source])
admin.site.register(Provider)
