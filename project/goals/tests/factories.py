from datetime import datetime

import factory

from ..models import Athlete, Entry, Goal


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goal

    year = 2022
    month = 4
    hours = 10


class AthleteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Athlete
        django_get_or_create = ("strava_id",)

    name = factory.Faker("name")
    strava_id = 123456


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entry

    athlete = factory.SubFactory(AthleteFactory)
    entry_id = 112233
    activity = "Running"
    date = datetime(2022, 4, 25, 3, 2, 1)
    time = 3600
    distance = 1000
    ascent = 100