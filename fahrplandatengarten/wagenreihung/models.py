from django.db import models

from fahrplandatengarten.core.models import JourneyStop


class Coach(models.Model):
    data = models.JSONField()

    def __str__(self):
        return f"Coach {self.data.get('uic')} ({self.pk})"


class CoachJourneyStop(models.Model):
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    journeystop = models.ForeignKey(JourneyStop, on_delete=models.CASCADE)

    data = models.JSONField(default=dict)
