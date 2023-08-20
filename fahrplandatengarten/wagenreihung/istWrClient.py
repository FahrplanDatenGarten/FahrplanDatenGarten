import requests
import pytz

from fahrplandatengarten.core.models import Journey, Stop, JourneyStop
from wagenreihung.models import Coach, CoachJourneyStop


class IstWrClient():
    def __init__(self, journeystop):
        self.journeystop = journeystop

    @property
    def date(self):
        if self.journeystop.planned_departure_time:
            return self.journeystop.planned_departure_time
        return self.journeystop.planned_arrival_time

    @property
    def url(self):
        return "https://ist-wr.noncd.db.de/wagenreihung/1.0/{}/{}".format(
            self.journeystop.journey.name.split(' ')[1],
            self.date.astimezone(pytz.timezone('Europe/Berlin')).strftime('%Y%m%d%H%M')
        )

    def import_wr(self):
        d = requests.get(self.url).json()

        if "data" not in d:
            return

        for group in d['data']['istformation']['allFahrzeuggruppe']:
            # TODO: delete coachjourneystops, which are no longer used
            for coach in group['allFahrzeug']:
                if coach['fahrzeugnummer'] == '':
                    continue
                c = Coach.objects.filter(data__uic=coach['fahrzeugnummer']).first()
                if not c:
                    c = Coach(data={'uic': coach['fahrzeugnummer']})
                c.data['type'] = coach['fahrzeugtyp']
                c.save()

                if coach['wagenordnungsnummer'] != '':
                    cjs = CoachJourneyStop.objects.filter(journeystop=self.journeystop, data__sequence_number=coach['wagenordnungsnummer']).first()
                    if not cjs:
                        cjs = CoachJourneyStop(journeystop=self.journeystop, coach=c)
                    elif cjs.coach != c:
                        cjs.coach = c
                else:
                    cjs, _ = CoachJourneyStop.objects.get_or_create(journeystop=self.journeystop, coach=c)
                    # TODO: better approach...

                cjs.data['trainset'] = group['fahrzeuggruppebezeichnung']
                cjs.data['sequence_number'] = coach['wagenordnungsnummer']
                cjs.save()

