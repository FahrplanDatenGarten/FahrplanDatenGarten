import datetime
import json
from json.decoder import JSONDecodeError
import pytz

import requests
from pyhafas import GeneralHafasError, HafasClient
from pyhafas.profile import DBProfile

from fahrplandatengarten.core.models import (Journey, JourneyStop, Provider, Source, StopID,
                         StopIDKind, Remark)


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
            if "Flug" in leg.name or "Os " in leg.name or "BUS" in leg.name or "R " in leg.name or "RB " in leg.name \
                    or "RE " in leg.name or "Sp " in leg.name or "STR " in leg.name or "BRB" in leg.name \
                    or "ARV" in leg.name or "S " in leg.name or "M " in leg.name:
                continue
            current_db_journeys = Journey.objects.filter(
                name=leg.name,
                date=leg.dateTime.date(),
                source=self.source
            )
            if current_db_journeys.count() == 0:
                Journey.objects.create(
                    trip_id=leg.id,
                    name=leg.name,
                    date=leg.dateTime.date(),
                    source=self.source,
                    cancelled=leg.cancelled
                )
            else:
                journey = current_db_journeys.first()
                if journey.cancelled != leg.cancelled:
                    journey.cancelled = leg.cancelled
                    journey.save()

    def get_trip_id(self, journey: Journey):
        if journey.trip_id is not None:
            return journey.trip_id

        lid_request = requests.get(
            url="https://reiseauskunft.bahn.de/bin/trainsearch.exe/dn",
            params={
                "L": "vs_json",
                "stationFilter": 80,
                "productClassFilter": 3,
                "date": journey.date.strftime("%d.%m.%Y"),
                "trainname": journey.name
            }
        )
        try:
            parsed_response = json.loads(lid_request.text[11:-1])
        except JSONDecodeError:
            return None
        trains = parsed_response['suggestions']
        if len(trains) == 0:
            return None
        first_train = trains[0]
        first_train_date = datetime.datetime.strptime(first_train['depDate'], '%d.%m.%Y').strftime('%d%m%Y')
        trip_id = f"1|{first_train['id']}|{first_train['cycle']}|{first_train['pool']}|{first_train_date}"

        journey.trip_id = trip_id
        journey.save()

        return trip_id

    def import_remarks(self, rems, obj):
        remarks = []
        existing_remark_pks = [r.pk for r in obj.remarks.all()]
        for rem in rems:
            remark = None
            try:
                remark = Remark.objects.filter(
                    remark_type=rem.remark_type,
                    code=rem.code,
                    subject=rem.subject,
                    text=rem.text,
                    priority=rem.priority,
                    trip_id=rem.trip_id
                )[0]
            except IndexError:
                remark = Remark(
                    remark_type=rem.remark_type,
                    code=rem.code,
                    subject=rem.subject,
                    text=rem.text,
                    priority=rem.priority,
                    trip_id=rem.trip_id
                )
                remark.save()
            remarks.append(remark)
            if remark.pk not in existing_remark_pks:
                obj.remarks.add(remark)

    def import_journey(self, journey: Journey):
        trip_id = self.get_trip_id(journey)
        if trip_id is None:
            return
        try:
            trip = self.hafasclient.trip(trip_id)
        except GeneralHafasError as e:
            return

        self.import_remarks(trip.remarks, journey)

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
                journey_stop = JourneyStop.objects.create(
                    stop=db_stop,
                    journey=journey,
                    planned_departure_time=stopover.departure,
                    actual_departure_delay=stopover.departureDelay,
                    planned_arrival_time=stopover.arrival,
                    actual_arrival_delay=stopover.arrivalDelay,
                    cancelled=stopover.cancelled)
            else:
                journey_stop = current_db_journeystops.first()
                if stopover.departure is not None and journey_stop.planned_departure_time != stopover.departure.astimezone(pytz.timezone('Europe/Berlin')):
                    journey_stop.planned_departure_time = stopover.departure
                if stopover.arrival is not None and journey_stop.planned_arrival_time != stopover.arrival.astimezone(pytz.timezone('Europe/Berlin')):
                    journey_stop.planned_arrival_time = stopover.arrival
                if journey_stop.cancelled != stopover.cancelled:
                    journey_stop.cancelled = stopover.cancelled
                if stopover.departureDelay is not None:
                    journey_stop.actual_departure_delay = stopover.departureDelay
                if stopover.arrivalDelay is not None:
                    journey_stop.actual_arrival_delay = stopover.arrivalDelay
                journey_stop.save()

            self.import_remarks(stopover.remarks, journey_stop)
