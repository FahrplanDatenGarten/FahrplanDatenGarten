from fahrplandatengarten.core.models import Stop
from django.db import models


class Connection(models.Model):
    stop = models.ManyToManyField(Stop)
    duration = models.DurationField(blank=True, null=True)
