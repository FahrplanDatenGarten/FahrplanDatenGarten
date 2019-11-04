from .hafasClient import HafasClient
from core.models import StopID, Stop, StopIDKind, Journey, Agency, Source, JourneyStop, StopName
from django.utils import timezone
from .hafasClient import HafasClient
import datetime
import pytz

class HafasImport:
    def __init__(self):
        self.hafasclient = HafasClient()
        self.db, _ = Agency.objects.get_or_create(name="db")
        self.dbapis, _ = Source.objects.get_or_create(name="dbapis")
        self.idkind, _ = StopIDKind.objects.get_or_create(name='eva')
        self.timezone = pytz.timezone("Europe/Berlin")

    def import_timetable(self, station, start_time=datetime.datetime.now(), duration=90):
        try:
            stopid, _ = StopID.objects.get_or_create(stop=station, kind=self.idkind)
        except StopID.MultipleObjectsReturned:
            stopid = StopID.objects.filter(stop=station, kind=self.idkind).first()
        res = self.hafasclient.stationBoard(station.stopname_set.first().name, duration=90)
        if len(res['svcResL']) != 0:
            if 'jnyL' in res['svcResL'][0]['res']:
                journeys = res['svcResL'][0]['res']['jnyL']
                for journey in journeys:
                    dbJourney, _ = Journey.objects.update_or_create(
                        journey_id=journey['jid'],
                        source=self.dbapis,
                        agency=self.db
                    )

    def import_journey(self, journey):
        journeyDetails = self.hafasclient.journeyDetails(journey.journey_id)['svcResL'][0]['res']
        if not journeyDetails.get('journey') is None:
            date = self.timezone.localize(datetime.datetime.strptime(journeyDetails['journey']['date'], "%Y%m%d"), is_dst=None)
            journey.name=journeyDetails['common']['prodL'][0]['name']
            journey.date=date
            journey.save()
            stops = journeyDetails['journey']['stopL']
            for stop in stops:
                if stop.get("dTimeS") is not None:
                    dTimeS = date + self.hafasclient.strpDelta(stop.get("dTimeS")[-6:])
                else:
                    dTimeS = None
                if stop.get("aTimeS") is not None:
                    aTimeS = date + self.hafasclient.strpDelta(stop.get("aTimeS")[-6:])
                else:
                    aTimeS = None

                if stop.get("dTimeR") is not None:
                    dTimeR = date + self.hafasclient.strpDelta(stop.get("dTimeR")[-6:])
                else:
                    dTimeR = None
                if stop.get("aTimeR") is not None:
                    aTimeR = date + self.hafasclient.strpDelta(stop.get("aTimeR")[-6:])
                else:
                    aTimeR = None

                name = journeyDetails['common']['locL'][stop['locX']]['name']
                dbStopName = StopName.objects.filter(
                    name=name,
                    source=self.dbapis
                ).first()
                if (dbStopName is None):
                    print("The Stop {} could not be found!".format(name))
                else:
                    dbStop = dbStopName.stop
                    if JourneyStop.objects.filter(stop=dbStop, journey=journey).count() == 0:
                        JourneyStop.objects.create(stop=dbStop, journey=journey,
                        planned_departure_time=dTimeS,
                        actual_departure_time=dTimeR,
                        planned_arrival_time=aTimeS,
                        actual_arrival_time=aTimeR)
                    else:
                        journeyStop = JourneyStop.objects.get(stop=dbStop, journey=journey)
                        if 'dTimeR' in stop:
                            journeyStop.actual_departure_time = dTimeR
                        if 'aTimeR' in stop:
                            journeyStop.actual_arrival_time = aTimeR
                        journeyStop.save()
