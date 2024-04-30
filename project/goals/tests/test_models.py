from datetime import date

import pendulum
import pytest

from ..models import Activities, Athletes, Goals
from .factories import AthleteFactory, EntryFactory, GoalFactory

pytestmark = pytest.mark.django_db


def test_goal_str():
    goal = GoalFactory()
    assert str(goal) == f"{goal.year} / {goal.month} / {goal.hours}"


def test_goal_current():
    GoalFactory(year=2022, month=2, hours=20)
    GoalFactory(year=2022, month=3, hours=30)
    GoalFactory(year=2022, month=4, hours=40)

    actual = Goals.objects.get_goal(2022, 4)

    assert actual == 40


def test_goal_not_set():
    GoalFactory()

    actual = Goals.objects.get_goal(1999, 4)

    assert actual == 0


def test_athlete_str():
    athlete = AthleteFactory()
    assert str(athlete) == athlete.name


def test_entry_str():
    entry = EntryFactory()
    assert str(entry) == f"{entry.date}: {entry.athlete}"


def test_entry_week_stats():
    EntryFactory()
    EntryFactory()
    EntryFactory(date=date(2022, 4, 1))

    actual = Activities.objects.week_stats(pendulum.date(2022, 4, 25))

    assert actual == {1: {"moving_time": 60, "num_activities": 2, "distance": 2, "ascent": 20}}


def test_entry_month_stats():
    EntryFactory()
    EntryFactory()
    EntryFactory(date=date(2022, 5, 1))

    actual = Activities.objects.month_stats(pendulum.date(2022, 4, 25))

    assert actual.count() == 1
    assert actual[0]["moving_time"] == 60
    assert actual[0]["num_activities"] == 2
    assert actual[0]["distance"] == 2
    assert actual[0]["ascent"] == 20


def test_entry_month_stats_ordering_by_moving_time():
    a2 = AthleteFactory(strava_id=2)
    a1 = AthleteFactory(strava_id=1)
    EntryFactory(athlete=a2)
    EntryFactory(athlete=a1)
    EntryFactory(athlete=a1)

    actual = Activities.objects.month_stats(pendulum.date(2022, 4, 25))
    print(actual)
    assert actual.count() == 2
    assert actual[0]["athlete_name"] == a1.name
    assert actual[0]["moving_time"] == 60

    assert actual[1]["athlete_name"] == a2.name
    assert actual[1]["moving_time"] == 30


def test_entry_total_time():
    EntryFactory()
    EntryFactory()
    EntryFactory(date=date(2022, 5, 1))

    actual = Activities.objects.total_time(pendulum.date(2022, 4, 25))

    assert actual == 1
