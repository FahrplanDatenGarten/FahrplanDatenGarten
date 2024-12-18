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


class Remark(models.Model):
    remark_type = models.CharField(null=True, blank=True, max_length=50)
    code = models.TextField(null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    priority = models.IntegerField(null=True, blank=True)
    trip_id = models.CharField(null=True, blank=True, max_length=200)

    def __str__(self):
        print(self.__dict__)
        return " - ".join([str(v) for k, v in self.__dict__.items() if v is not None and k not in ['_state', 'id']])


class Stop(models.Model):
    ifopt = models.CharField(max_length=255, null=True, blank=True)
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

    def __str__(self):
        return f"{self.name} ({self.pk})"


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
    trip_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    stop = models.ManyToManyField(Stop, through='JourneyStop', blank=True)
    date = models.DateField(null=True, blank=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    cancelled = models.BooleanField(default=False)
    remarks = models.ManyToManyField(Remark, blank=True)

    def __str__(self):
        return self.name

    def first_date(self):
        return sorted(self.journeystop_set.all(),
                      key=lambda x: x.earlier_time())[0].earlier_time()


class JourneyStop(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    planned_arrival_time = models.DateTimeField(null=True, blank=True)
    planned_departure_time = models.DateTimeField(null=True, blank=True)
    actual_arrival_delay = models.DurationField(null=True, blank=True)
    actual_departure_delay = models.DurationField(null=True, blank=True)
    cancelled = models.BooleanField(default=False)
    planned_platform = models.CharField(null=True, blank=True, max_length=255)
    actual_platform = models.CharField(null=True, blank=True, max_length=255)
    remarks = models.ManyToManyField(Remark, blank=True)

    def earlier_time(self):
        if self.planned_arrival_time:
            return self.planned_arrival_time

        if self.planned_departure_time:
            return self.planned_departure_time

    def actual_earlier_time(self) -> Optional[datetime.datetime]:
        if self.get_actual_arrival_time():
            return self.get_actual_arrival_time()

        if self.get_actual_departure_time():
            return self.get_actual_departure_time()

        return None

    def get_delay(self):
        if self.actual_arrival_delay is not None:
            return self.actual_arrival_delay
        elif self.actual_departure_delay is not None:
            return self.actual_departure_delay
        return None

    def get_actual_arrival_time(self) -> Optional[datetime.datetime]:
        if self.actual_arrival_delay is not None:
            return self.planned_arrival_time + self.actual_arrival_delay
        else:
            return None

    def get_actual_departure_time(self) -> Optional[datetime.datetime]:
        if self.actual_departure_delay is not None:
            return self.planned_departure_time + self.actual_departure_delay
        else:
            return None

    def get_actual_platform(self) -> Optional[str]:
        if self.actual_platform:
            return self.actual_platform
        else:
            return self.planned_platform

    def __str__(self):
        return f"{self.journey.name}@{self.stop.name} ({self.pk})"
