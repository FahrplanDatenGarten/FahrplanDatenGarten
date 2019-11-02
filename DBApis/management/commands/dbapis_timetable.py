# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import requests
from hashlib import md5
import base64
import json
from Crypto.Cipher import AES
import codecs
import datetime
import re

from core.models import StopID, Stop, Journey, Agency, Source, JourneyStop, StopName


class Command(BaseCommand):
    help = 'Imports the Timetable from DB API'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs='?', type=str)

    def handle(self, *args, **options):
        stop = Stop.objects.filter(stopname__name=options['name']).first()
        bahnapi = BahnAPI()
        db=Agency.objects.filter(name="db").first()
        dbapis=Source.objects.filter(name="dbapis").first()
        stopID = StopID.objects.filter(stop=stop, kind__name="eva").first()
        # res = bahnapi.stationBoard("Berlin Hbf", duration=40)
        res = bahnapi.stationBoard(stop.stopname_set.filter(source__name='dbapis').first().name, duration=90)
        if len(res['svcResL']) != 0:
            if 'jnyL' in res['svcResL'][0]['res']:
                journeys = res['svcResL'][0]['res']['jnyL']
                for journey in journeys:
                    journeyDetails = bahnapi.journeyDetails(journey['jid'])['svcResL'][0]['res']
                    date=datetime.datetime.strptime(journeyDetails['journey']['date'], "%Y%m%d")
                    dbJourney, _ = Journey.objects.update_or_create(
                        name=journeyDetails['common']['prodL'][0]['name'],
                        date=date,
                        journey_id=journey['jid'],
                        source=dbapis,
                        agency=db
                    )
                    stops = journeyDetails['journey']['stopL']
                    for stop in stops:
                        if stop.get("dTimeS") is not None:
                            dTimeS = date + bahnapi.strpDelta(stop.get("dTimeS")[-6:])
                        else:
                            dTimeS = None
                        if stop.get("aTimeS") is not None:
                            aTimeS = date + bahnapi.strpDelta(stop.get("aTimeS")[-6:])
                        else:
                            aTimeS = None
                            print('No sceduled arrival')

                        if stop.get("dTimeR") is not None:
                            dTimeR = date + bahnapi.strpDelta(stop.get("dTimeR")[-6:])
                        else:
                            print('No actual departure')
                            dTimeR = None

                        if stop.get("aTimeR") is not None:
                            aTimeR = date + bahnapi.strpDelta(stop.get("aTimeR")[-6:])
                        else:
                            print('No actual arrival')
                            aTimeR = None

                        name = journeyDetails['common']['locL'][stop['locX']]['name']
                        dbStopName = StopName.objects.filter(
                            name=name,
                            source=dbapis
                        ).first()
                        if (dbStopName is None):
                            print("The Stop {} could not be found!".format(name))
                        else:
                            dbStop = dbStopName.stop
                            if JourneyStop.objects.filter(stop=dbStop, journey=dbJourney).count() == 0:
                                JourneyStop.objects.create(stop=dbStop, journey=dbJourney,
                                planned_departure_time=dTimeS,
                                actual_departure_time=dTimeR,
                                planned_arrival_time=aTimeS,
                                actual_arrival_time=aTimeR)
                            else:
                                journeyStop = JourneyStop.objects.get(stop=dbStop, journey=dbJourney)
                                if 'dTimeR' in stop:
                                    journeyStop.actual_departure_time = dTimeR
                                if 'aTimeR' in stop:
                                    journeyStop.actual_arrival_time = aTimeR


class BahnAPI():
    debug = False
    base_url = "https://reiseauskunft.bahn.de/bin/mgate.exe?checksum={checksum}"
    redtnCards = {"": 0, "25_1": 1, "25_2": 2, "50_1": 3, "50_2": 4}
    traveler_types = {"adult": "E", "child": "K", "infant": "B"}
    aid = "rGhXPq+xAlvJd8T8cMnojdD0IoaOY53X7DPAbcXYe5g="
    aid2 = "n91dB8Z77MLdoR0K"
    key = bytes([97, 72, 54, 70, 56, 122, 82, 117, 105, 66, 110, 109, 51, 51, 102, 85])

    def searchLocation(self, term):
        data = {
            "svcReqL": [{"meth": "LocMatch", "req": {"input": {"field": "S", "loc": {"name": term, "type": "S"}}}}]}
        search_request = self.sendPostRequest(data)
        # print(search_request.text)
        response = self.cleanResponse(search_request.json())
        search_results = []
        if response["svcResL"][0]["err"] == "OK":
            for response_part in response["svcResL"]:
                if response_part["err"] == "OK" and response_part["meth"] == "LocMatch":
                    for result in response_part["res"]["match"]["locL"]:
                        search_results.append({k: v for k, v in result.items() if k in ["lid", "name", "type"]})
        return search_results

    def journeyDetails(self, journeyId):
        data = {"svcReqL": [{
            "meth": "JourneyDetails",
            "req": {"jid": journeyId}
        }]}
        search_request = self.sendPostRequest(data)
        response = self.cleanResponse(search_request.json())
        return response

    def stationBoard(self, stationName, start_datetime=datetime.datetime.now(), duration=60):
        station = self.searchLocation(stationName)[0]
        data = {"svcReqL": [
            {
             "meth": "StationBoard",
             "req": {
                 "date": start_datetime.strftime("%Y%m%d"),
                 "dur": duration,
                 "stbLoc": {
                     "lid": station['lid']
                 },
                 "getPasslist": False,
                 "time": start_datetime.strftime("%H%M%S"),
                 "jnyFltrL": [
                     {
                         "mode": "INC",
                         "type": "PROD",
                         "value": "7"
                     }
                 ],
             }
             }
        ]
        }
        search_request = self.sendPostRequest(data)
        response = self.cleanResponse(search_request.json())
        return response

    def parse_timedelta(self, time_str):
        regex = re.compile(r'(?P<days>\d{2})(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2})')
        if len(time_str) == 6:
            time_str = "00" + time_str
        parts = regex.match(time_str)
        if not parts:
            return
        parts = parts.groupdict()
        time_params = {name: int(amount) for name, amount in parts.items()}
        return datetime.datetime.timedelta(**time_params)

    def getFinalTime(self, start_date, duration):
        dur = self.parse_timedelta(duration)
        return datetime.datetime.strptime(start_date, "%Y%m%d") + dur

    def sendPostRequest(self, data, headers={}):
        data["auth"] = {"aid": self.aid2, "type": "AID"}  # from res/raw/haf_config.properties of DBNavigator
        data["client"] = {"id": "DB", "name": "DB Navigator", "type": "IPH", "v": "19040000", "os": "iOS 13.1.2"}
        data["ver"] = "1.15"
        data["ext"] = "DB.R19.04.a"
        data["lang"] = "de"
        data = json.dumps(data)
        chk = self.generateChecksum(data)
        url = self.base_url.format(checksum=chk)
        req = requests.post(url, data=data,
                            headers={"User-Agent": "DB Navigator/19.10.04 (iPhone; iOS 13.1.2; Scale/2.00)",
                                     "Authorization": "Basic Og== ", "Content-Type": "application/json"})
        return req

    def cleanResponse(self, data):
        return data

    def generateChecksum(self, data):
        to_hash = data + self.getSecret()
        to_hash = to_hash.encode("utf-8")
        return md5(to_hash).hexdigest()

    def getSecret(self):
        unpad = lambda s: s[:-ord(s[len(s) - 1:])]
        enc = base64.b64decode(self.aid)
        iv = codecs.decode("00" * 16, "hex")
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        dec = unpad(cipher.decrypt(enc).decode("utf-8"))
        return dec

    def strpDelta(self, string):
        return datetime.timedelta(hours=int(string[-6:-4]), minutes=int(string[-4:-2]), seconds=int(string[-2:]))
