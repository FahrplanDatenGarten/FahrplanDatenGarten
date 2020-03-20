from django.db import models

# Create your models here.


class Stop(models.Model):
    pass


class StopIDKind(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Agency(models.Model):
    name = models.CharField(max_length=255)
    used_id_kind = models.ManyToManyField(StopIDKind, blank=True)

    class Meta:
        verbose_name_plural = "agencies"

    def __str__(self):
        return self.name


class StopName(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ["-priority"]

    def __str__(self):
        return self.name


class StopID(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    kind = models.ForeignKey(
        StopIDKind,
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    def __str__(self):
        return self.name


class StopLocation(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    country = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)

    class Meta:
        ordering = ["-priority"]


class Journey(models.Model):
    name = models.CharField(max_length=255, null=True)
    stop = models.ManyToManyField(Stop, through='JourneyStop')
    date = models.DateField(null=True)
    journey_id = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

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
    actual_arrival_time = models.DateTimeField(null=True)
    actual_departure_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ["planned_arrival_time"]

    def earlier_time(self):
        if self.planned_arrival_time:
            return self.planned_arrival_time

        if self.planned_departure_time:
            return self.planned_departure_time
