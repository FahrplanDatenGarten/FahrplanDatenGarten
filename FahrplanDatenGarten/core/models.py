import datetime
from typing import Optional

from django.db import models
from django_countries.fields import CountryField


class Provider(models.Model):
    friendly_name = models.CharField(max_length=255)
    internal_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.friendly_name


class Source(models.Model):
    friendly_name = models.CharField(max_length=255)
    internal_name = models.CharField(max_length=255, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)

    def __str__(self):
        return self.friendly_name


class Stop(models.Model):
    ifopt = models.CharField(max_length=255)
    country = CountryField()
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True)
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True)
    name = models.CharField(max_length=255)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    has_long_distance_traffic = models.BooleanField()


class StopIDKind(models.Model):
    name = models.CharField(max_length=255, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class StopID(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=255)
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE)
    kind = models.ForeignKey(
        StopIDKind,
        on_delete=models.CASCADE)

    def __str__(self):
        return self.external_id


class Journey(models.Model):
    name = models.CharField(max_length=255, null=True)
    stop = models.ManyToManyField(Stop, through='JourneyStop')
    date = models.DateField(null=True)
    journey_id = models.CharField(max_length=255, unique=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        if self.name is not None:
            return self.name
        return self.journey_id

    def first_date(self):
        return sorted(self.journeystop_set.all(),
                      key=lambda x: x.earlier_time())[0].earlier_time()


class JourneyStop(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    planned_arrival_time = models.DateTimeField(null=True)
    planned_departure_time = models.DateTimeField(null=True)
    actual_arrival_delay = models.DurationField(null=True)
    actual_departure_delay = models.DurationField(null=True)
    cancelled = models.BooleanField(default=False)

    def earlier_time(self):
        if self.planned_arrival_time:
            return self.planned_arrival_time

        if self.planned_departure_time:
            return self.planned_departure_time

    def get_actual_arrival_time(self) -> Optional[datetime.datetime]:
        if self.actual_arrival_delay is not None:
            return self.planned_arrival_time + self.actual_arrival_delay
        else:
            return None

    def get_actual_departure_time(self) -> datetime.datetime:
        if self.actual_arrival_delay is not None:
            return self.planned_departure_time + self.actual_departure_delay
        else:
            return None
