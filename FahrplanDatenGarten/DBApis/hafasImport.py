import datetime

from core.models import (Journey, JourneyStop, Provider, Source, StopID,
                         StopIDKind)
from pyhafas import GeneralHafasError, HafasClient
from pyhafas.profile import DBProfile


class HafasImport:
    def __init__(self):
        self.hafasclient = HafasClient(DBProfile())
        self.provider = Provider.objects.get(internal_name="db")
        self.source, _ = Source.objects.get_or_create(
            internal_name="db_hafas",
            friendly_name="Deutsche Bahn HAFAS",
            provider=self.provider)
        self.idkind, _ = StopIDKind.objects.get_or_create(
            name='eva', provider=self.provider)

    def import_timetable(
            self,
            station,
            duration=90):
        stopid = StopID.objects.get(
            stop=station,
            kind=self.idkind)
        departure_legs = self.hafasclient.departures(
            station=stopid.external_id,
            date=datetime.datetime.now(),
            duration=duration,
            products={
                'long_distance_express': True,
                'long_distance': True,
                'regional_express': False,
                'regional': False,
                'suburban': False,
                'bus': False,
                'ferry': False,
                'subway': False,
                'tram': False,
                'taxi': False
            }
        )
        for leg in departure_legs:
            current_db_journeys = Journey.objects.filter(
                name=leg.name,
                date=leg.dateTime.date(),
                journey_id=leg.id,
                source=self.source
            )
            if current_db_journeys.count() == 0:
                Journey.objects.create(
                    name=leg.name,
                    date=leg.dateTime.date(),
                    journey_id=leg.id,
                    source=self.source,
                    cancelled=leg.cancelled
                )
            else:
                journey = current_db_journeys.first()
                if journey.cancelled != leg.cancelled:
                    journey.cancelled = leg.cancelled
                    journey.save()

    def import_journey(self, journey):
        try:
            trip = self.hafasclient.trip(journey.journey_id)
        except GeneralHafasError:
            return
        for stopover in trip.stopovers:
            eva_id = stopover.stop.id[-8:]
            db_stop_id = StopID.objects.filter(
                external_id=eva_id,
                kind__name='eva',
                kind__provider=self.provider
            ).first()
            if db_stop_id is None:
                print(
                    "The Stop {} with ID {} could not be found!".format(
                        stopover.stop.name, eva_id))
                continue
            db_stop = db_stop_id.stop
            current_db_journeystops = JourneyStop.objects.filter(
                stop=db_stop,
                journey=journey
            )
            if current_db_journeystops.count() == 0:
                JourneyStop.objects.create(
                    stop=db_stop,
                    journey=journey,
                    planned_departure_time=stopover.departure,
                    actual_departure_delay=stopover.departureDelay,
                    planned_arrival_time=stopover.arrival,
                    actual_arrival_delay=stopover.arrivalDelay,
                    cancelled=stopover.cancelled)
            else:
                journey_stop = current_db_journeystops.first()
                if journey_stop.cancelled != stopover.cancelled:
                    journey_stop.cancelled = stopover.cancelled
                if stopover.departureDelay is not None:
                    journey_stop.actual_departure_delay = stopover.departureDelay
                if stopover.arrivalDelay is not None:
                    journey_stop.actual_arrival_delay = stopover.arrivalDelay
                journey_stop.save()
