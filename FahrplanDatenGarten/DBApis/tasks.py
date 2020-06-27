from celery.schedules import crontab
from celery.task import periodic_task, task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from pyhafas import HafasClient
from pyhafas.profile import DBProfile

from core.models import Journey, Stop, StopName, StopID, StopLocation, Agency, Source, StopIDKind
from DBApis.hafasImport import HafasImport

logger = get_task_logger(__name__)


@periodic_task(
    run_every=(
        crontab(
            hour=settings.PERIODIC_IMPORT_TIMETABLES[0],
            minute=settings.PERIODIC_IMPORT_TIMETABLES[1])),
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


@task(name="dbapis_importstations_parse_station_row")
def dbapis_importstations_parse_station_row(row, agency_pk, source_pk, kind_pk):
    hafas_client = HafasClient(DBProfile())

    agency = Agency.objects.get(pk=agency_pk)
    source = Source.objects.get(pk=source_pk)
    kind = StopIDKind.objects.get(pk=kind_pk)
    if row['EVA_NR'] == '':
        return
    stop = Stop.objects.filter(
        stopid__name=row['EVA_NR'],
        stopid__kind__in=agency.used_id_kind.all()
    ).first()
    if stop is None:
        stop = Stop()
        stop.save()
    StopName.objects.get_or_create(
        name=row['NAME'], stop=stop, source=source)
    StopID.objects.get_or_create(
        stop=stop,
        name=row['EVA_NR'],
        source=source,
        kind=kind
    )
    try:
        StopLocation.objects.get(
            stop=stop,
            source=source
        )
    except ObjectDoesNotExist:
        try:
            hafasLocation = hafas_client.locations(row['EVA_NR'])[0]
            StopLocation.objects.create(
                stop=stop,
                latitude=hafasLocation.latitude,
                longitude=hafasLocation.longitude,
                source=source
            )
        except IndexError:
            return
