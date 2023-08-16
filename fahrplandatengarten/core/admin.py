from django.contrib import admin

# Register your models here.
from .models import (Journey, JourneyStop, Provider, Source, Stop, StopID,
                     StopIDKind, Remark)


class StopIDAdminInline(admin.TabularInline):
    model = StopID


class StopAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = (
        'name',
        'primary_stop_id')
    inlines = [StopIDAdminInline]

    @staticmethod
    def primary_stop_id(obj):
        return obj.stopid_set.first().external_id


class JourneystopAdminInline(admin.TabularInline):
    model = JourneyStop
    autocomplete_fields = ['stop', 'remarks']
    fields = (
        'stop',
        'planned_arrival_time',
        'planned_departure_time',
        'actual_arrival_delay',
        'actual_departure_delay',
        'remarks'
    )


class JourneyAdmin(admin.ModelAdmin):
    inlines = (JourneystopAdminInline,)
    autocomplete_fields = ['remarks']
    list_display = (
        'name',
        'date',
        'cancelled',
        'source',
    )
    list_filter = (
        'date',
        'cancelled',
    )
    search_fields = ('name',)


class RemarkAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'remark_type',
        'code',
        'subject',
        'text',
        'priority',
        'trip_id',
    )
    list_filter = (
        'remark_type',
        'code',
    )
    search_fields = ('subject','text',)


admin.site.register(Stop, StopAdmin)
admin.site.register(Journey, JourneyAdmin)
admin.site.register(Remark, RemarkAdmin)
admin.site.register([StopID, StopIDKind, Source, Provider])
