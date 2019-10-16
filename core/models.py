from django.db import models

# Create your models here.
class Stop(models.Model):
    ifopt = models.CharField(max_length=255, primary_key=True)

class Source(models.Model):
    name = models.CharField(max_length=255)

class Agency(models.Model):
    name = models.CharField(max_length=255)

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
    source_stop_id = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    source_stop_id_type = models.CharField(max_length=255, null=True)

class Journey(models.Model):
    name = models.CharField(max_length=255)
    stop = models.ManyToManyField(Stop, through='JourneyStop')
    date = models.DateField()
    journey_id = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)

class JourneyStop(models.Model):
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    planned_arrival_time = models.DateTimeField(null=True)
    planned_departure_time = models.DateTimeField(null=True)
    actual_arrival_time = models.DateTimeField(null=True)
    actual_departure_time = models.DateTimeField(null=True)

    class Meta:
        ordering = ["planned_arrival_time"]
