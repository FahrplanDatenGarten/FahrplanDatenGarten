from fahrplandatengarten.core.admin import StopAdmin
from django.contrib import admin

from .models import Connection


class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        'duration',
        'stop_list')

    def stop_list(self, obj):
        return ", ".join([str(s.name)
                          for s in obj.stop.all()])


admin.site.register(Connection, ConnectionAdmin)
