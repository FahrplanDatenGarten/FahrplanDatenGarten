from django.contrib import admin

# Register your models here.
from .models import Stop, StopID, StopIDKind, StopName, StopLocation, Source, Agency, Journey, JourneyStop

class StopnameAdminInline(admin.TabularInline):
    model = StopName

class StopIDAdminInline(admin.TabularInline):
    model = StopID

class StoplocationAdminInline(admin.TabularInline):
    model = StopLocation

class StopAdmin(admin.ModelAdmin):
    list_display = ('primary_stop_name', 'primary_stop_id', 'primary_stop_location')
    inlines = (StopnameAdminInline, StopIDAdminInline, StoplocationAdminInline)

    def primary_stop_name(self, obj):
        return obj.stopname_set.first().name

    def primary_stop_id(self, obj):
        return obj.stopid_set.first().name

    def primary_stop_location(self, obj):
        return obj.stoplocation_set.first()

admin.site.register(Stop, StopAdmin)
admin.site.register([StopID, StopIDKind, StopName, StopLocation, Source, Agency, Journey, JourneyStop])
