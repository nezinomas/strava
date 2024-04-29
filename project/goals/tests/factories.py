from datetime import date

import factory

from ..models import AthleteModel, EntryModel, GoalModel


class GoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GoalModel

    year = 2022
    month = 4
    hours = 10


class AthleteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AthleteModel
        django_get_or_create = ("strava_id",)

    name = factory.Faker("name")
    strava_id = 1


class EntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EntryModel

    athlete = factory.SubFactory(AthleteFactory)
    date = date(2022, 4, 25)
    moving_time = 30
    distance = 1
    ascent = 10