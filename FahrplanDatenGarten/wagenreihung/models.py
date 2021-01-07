from django.db import models

from core.models import JourneyStop


class Coach(models.Model):
    data = models.JSONField()


class CoachJourneyStop(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    journeystop = models.ForeignKey(JourneyStop, on_delete=models.CASCADE)

    data = models.JSONField(default=dict)
