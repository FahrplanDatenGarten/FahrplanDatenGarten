import datetime

from celery.schedules import crontab
from celery.utils.log import get_task_logger
from core.models import JourneyStop
from django.conf import settings
from django.db.models import Q

from FahrplanDatenGarten.celery import app
from wagenreihung.istWrClient import IstWrClient

logger = get_task_logger(__name__)


@app.on_after_finalize.connect
def setup_wagenreihung_configure_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(
            hour=settings.PERIODIC_IMPORT_WAGENREIHUNGEN[0],
            minute=settings.PERIODIC_IMPORT_WAGENREIHUNGEN[1]),
        import_all_wagenreihungen.s()
    )

@app.task(name="import_all_wagenreihungen", ignore_result=True)
def import_all_wagenreihungen():
    wr_after = datetime.datetime.now() - datetime.timedelta(hours=3)
    for journeystop in JourneyStop.objects.filter(Q(planned_arrival_time__gte=wr_after) | Q(planned_departure_time__gte=wr_after)).all():
        import_wagenreihung.delay(journeystop.pk)

@app.task(name="import_wagenreihung")
def import_wagenreihung(journeystop_pk):
    istWrClient = IstWrClient(JourneyStop.objects.get(pk=journeystop_pk))
    istWrClient.import_wr()

