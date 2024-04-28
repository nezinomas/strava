from django.db import models
from django.utils.text import slugify
from .managers import AthleteManager, EntryManager


class Goal(models.Model):
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.year} / {self.month}"


class Athlete(models.Model):
    name = models.CharField(max_length=255)
    strava_id = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    objects = AthleteManager.as_manager()

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class Entry(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    entry_id = models.PositiveIntegerField()
    activity = models.CharField(max_length=255)
    date = models.DateField()
    time = models.PositiveIntegerField()
    distance = models.PositiveIntegerField(default=0)
    ascent = models.PositiveIntegerField(default=0)

    objects = EntryManager.as_manager()

    def __str__(self):
        return f"{self.date}: {self.athlete}"
