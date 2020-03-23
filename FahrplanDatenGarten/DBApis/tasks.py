from celery.decorators import periodic_task, task
from celery.task.schedules import crontab
from celery.utils.log import get_task_logger
from django.conf import settings

from core.models import Journey, Stop
from DBApis.hafasImport import HafasImport

logger = get_task_logger(__name__)


@periodic_task(
    run_every=(
        crontab(
            hour=settings.PERIODIC_IMPORT_TIMETABLES[0],
            minute=settings.PERIODIC_IMPORT_JOURNEYS[1])),
    name="import_all_timetables",
    ignore_result=True)
def import_all_timetables():
    for stop in Stop.objects.filter(stopid__kind__name='eva').all():
        import_timetable.delay(stop.pk)


@task(name="import_timetable")
def import_timetable(stop_pk):

    hafasimport = HafasImport()
    hafasimport.import_timetable(Stop.objects.get(pk=stop_pk))


@periodic_task(
    run_every=(
        crontab(
            hour=settings.PERIODIC_IMPORT_JOURNEYS[0],
            minute=settings.PERIODIC_IMPORT_JOURNEYS[1])),
    name="import_all_journeys",
    ignore_result=True)
def import_all_journeys():
    for journey in Journey.objects.filter(agency__name='db').all():
        import_journey.delay(journey.pk)


@task(name="import_journey")
def import_journey(journey_pk):
    hafasimport = HafasImport()
    hafasimport.import_journey(Journey.objects.get(pk=journey_pk))
