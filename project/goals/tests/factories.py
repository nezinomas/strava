from datetime import date

import factory

from ..models import Athletes, Activities, Goal, Logs


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Goal

    year = 2022
    month = 4
    hours = 10


class AthleteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Athletes
        django_get_or_create = ("strava_id",)

    name = factory.Faker("name")
    strava_id = 1


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Activities

    athlete = factory.SubFactory(AthleteFactory)
    date = date(2022, 4, 25)
    moving_time = 30
    distance = 1
    num_activities = 1
    ascent = 10


class LogSuccessFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Logs

    status = "Success"
    message = None


class LogFailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Logs

    status = "Failed"
    message = "Exception message"
