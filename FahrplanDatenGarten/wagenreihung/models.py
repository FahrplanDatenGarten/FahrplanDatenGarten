from django.db import models

from core.models import JourneyStop


class Coach(models.Model):
    metadata = models.JSONField()


class CoachJourneyStop(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    journeystop = models.ForeignKey(JourneyStop, on_delete=models.CASCADE)

    section = models.CharField(null=True, max_length=255)
    trainset_number = models.IntegerField(null=True)
    sequence_number = models.IntegerField(null=True)
