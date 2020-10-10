from django.contrib import admin

# Register your models here.
from .models import (Journey, JourneyStop, Provider, Source, Stop, StopID,
                     StopIDKind)


class StopIDAdminInline(admin.TabularInline):
    model = StopID


class StopAdmin(admin.ModelAdmin):
    list_display = (
        'primary_stop_name',
        'primary_stop_id',
        'primary_stop_location')
    inlines = [StopIDAdminInline]

    @staticmethod
    def primary_stop_name(obj):
        return obj.stopname_set.first().name

    @staticmethod
    def primary_stop_id(obj):
        return obj.stopid_set.first().name

    def primary_stop_location(self, obj):
        return obj.stoplocation_set.first()


class JourneystopAdminInline(admin.TabularInline):
    model = JourneyStop
    # fields = ('primary_stop_name', 'planned_arrival_time', 'planned_departure_time', 'actual_arrival_time', 'actual_departure_time')
    fields = (
        'stop',
        'planned_arrival_time',
        'planned_departure_time',
        'actual_arrival_delay',
        'actual_departure_delay')

    # readonly_fields = ('primary_stop_name', )

    def primary_stop_name(self, obj):
        return obj.stop.stopname_set.first().name


class JourneyAdmin(admin.ModelAdmin):
    inlines = (JourneystopAdminInline,)


admin.site.register(Stop, StopAdmin)
admin.site.register(Journey, JourneyAdmin)
admin.site.register([StopID, StopIDKind, Source])
admin.site.register(Provider)
