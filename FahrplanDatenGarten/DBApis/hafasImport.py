import datetime

import pytz
from pyhafas import HafasClient
from pyhafas.profile import DBProfile

from core.models import (Agency, Journey, Source, StopID,
                         StopIDKind, JourneyStop)


class HafasImport:
    def __init__(self):
        self.hafasclient = HafasClient(DBProfile())
        self.db, _ = Agency.objects.get_or_create(name="db")
        self.dbapis, _ = Source.objects.get_or_create(name="dbapis")
        self.idkind, _ = StopIDKind.objects.get_or_create(name='eva')
        self.timezone = pytz.timezone("Europe/Berlin")

    def import_timetable(
            self,
            station,
            duration=90):
        try:
            stopid, _ = StopID.objects.get_or_create(
                stop=station, kind=self.idkind)
        except StopID.MultipleObjectsReturned:
            stopid = StopID.objects.filter(
                stop=station, kind=self.idkind).first()
        departure_journeys = self.hafasclient.departures(
            station=stopid.name,
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
        for journey in departure_journeys:
            dbJourney, _ = Journey.objects.update_or_create(
                journey_id=journey.id,
                source=self.dbapis,
                agency=self.db
            )

    def import_journey(self, journey):
        try:
            trip = self.hafasclient.trip(journey.journey_id)
        except:  # TODO: Implement correct Exception when pyhafas has them
            return
        journey.name = trip.name
        journey.date = trip.departure.date()
        journey.save()
        for stopover in trip.stopovers:
            eva_id = stopover.stop.id[-8:]
            dbStopID = StopID.objects.filter(
                name=eva_id,
                source=self.dbapis
            ).first()
            if dbStopID is None:
                print("The Stop {} with ID {} could not be found!".format(stopover.stop.name, eva_id))
                continue
            dbStop = dbStopID.stop
            if JourneyStop.objects.filter(
                    stop=dbStop, journey=journey).count() == 0:
                JourneyStop.objects.create(
                    stop=dbStop,
                    journey=journey,
                    planned_departure_time=stopover.departure,
                    actual_departure_time=stopover.departure + stopover.departureDelay if stopover.departureDelay is not None else None,
                    planned_arrival_time=stopover.arrival,
                    actual_arrival_time=stopover.arrival + stopover.arrivalDelay if stopover.arrivalDelay is not None else None)
            else:
                journeyStop = JourneyStop.objects.get(
                    stop=dbStop, journey=journey)
                if stopover.departureDelay is not None:
                    journeyStop.actual_departure_time = stopover.departure + stopover.departureDelay
                if stopover.arrivalDelay is not None:
                    journeyStop.actual_arrival_time = stopover.arrival + stopover.arrivalDelay
                journeyStop.save()
