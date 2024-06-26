from django.db import models

from .managers import AthleteManager, EntryManager, GoalManager


class Logs(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10)
    message = models.TextField(null=True, blank=True)


class Goals(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    hours = models.PositiveIntegerField()

    objects = GoalManager.as_manager()
    def __str__(self):
        return f"{self.year} / {self.month} / {self.hours}"


class Athletes(models.Model):
    name = models.CharField(max_length=255)
    strava_id = models.PositiveIntegerField(unique=True)

    objects = AthleteManager.as_manager()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class Activities(models.Model):
    athlete = models.ForeignKey(Athletes, on_delete=models.CASCADE)
    date = models.DateField()
    num_activities = models.IntegerField(default=1)
    moving_time = models.IntegerField(default=0)
    distance = models.IntegerField(default=0)
    ascent = models.IntegerField(default=0)

    objects = EntryManager.as_manager()

    def __str__(self):
        return f"{self.date}: {self.athlete}"
