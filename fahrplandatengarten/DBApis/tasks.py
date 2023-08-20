import datetime
from decimal import Decimal

from celery.schedules import crontab
from celery.utils.log import get_task_logger
from fahrplandatengarten.core.models import Journey, Provider, Source, Stop, StopID, StopIDKind
from fahrplandatengarten.DBApis.hafasImport import HafasImport
from django.conf import settings

from fahrplandatengarten.celery import app

logger = get_task_logger(__name__)


@app.on_after_finalize.connect
def setup_dbapis_configure_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(
            hour=settings.PERIODIC_IMPORT_TIMETABLES[0],
            minute=settings.PERIODIC_IMPORT_TIMETABLES[1]),
        import_all_timetables.s()
    )
    sender.add_periodic_task(
        crontab(
            hour=settings.PERIODIC_IMPORT_JOURNEYS[0],
            minute=settings.PERIODIC_IMPORT_JOURNEYS[1]),
        import_all_journeys.s()
    )


@app.task(name="import_all_timetables", ignore_result=True)
def import_all_timetables():
    for stop in Stop.objects.filter(
            provider__internal_name="db",
            has_long_distance_traffic=True).all():
        import_timetable.delay(stop.pk)


@app.task(name="import_timetable")
def import_timetable(stop_pk):
    hafasimport = HafasImport()
    hafasimport.import_timetable(Stop.objects.get(pk=stop_pk))


@app.task(name="import_all_journeys", ignore_result=True)
def import_all_journeys():
    for journey in Journey.objects.filter(
            source__internal_name='db_hafas',
            date__gte=datetime.date.today() - datetime.timedelta(days=1)
    ).all():
        import_journey.delay(journey.pk)


@app.task(name="import_journey")
def import_journey(journey_pk):
    hafasimport = HafasImport()
    hafasimport.import_journey(Journey.objects.get(pk=journey_pk))


@app.task(name="dbapis_importstations_parse_station_row")
def dbapis_importstations_parse_station_row(
        row, provider_pk, source_pk, kind_pk):
    provider = Provider.objects.get(pk=provider_pk)
    source = Source.objects.get(pk=source_pk)
    kind = StopIDKind.objects.get(pk=kind_pk)
    if row['EVA_NR'] == '' or row['IFOPT'] == '':
        return
    stop = Stop.objects.filter(
        stopid__external_id=row['EVA_NR'],
        stopid__kind=kind,
        stopid__kind__provider=provider
    ).first()
    if stop is None or stop.provider == provider:
        if stop is None:
            stop = Stop.objects.create(
                ifopt=row['IFOPT'],
                country=row['IFOPT'][:2],
                latitude=Decimal(row['Breite'].replace(',', '.')),
                longitude=Decimal(row['Laenge'].replace(',', '.')),
                name=row['NAME'],
                provider=provider,
                has_long_distance_traffic=row['Verkehr'] == "FV"
            )
            StopID.objects.get_or_create(
                stop=stop,
                external_id=row['EVA_NR'],
                source=source,
                kind=kind
            )
        else:
            stop.latitude = Decimal(row['Breite'].replace(',', '.'))
            stop.longitude = Decimal(row['Laenge'].replace(',', '.'))
            stop.name = row['NAME']
            stop.has_long_distance_traffic = row['Verkehr'] == "FV"
            stop.save()
        StopID.objects.get_or_create(
            stop=stop,
            external_id=row['EVA_NR'],
            source=source,
            kind=kind
        )
