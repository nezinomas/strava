from datetime import date

import pytest
import pendulum
from ..models import Athletes, Activities, Goals
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

    assert actual.hours == 40


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
    EntryFactory(date=date(2022, 4, 24))
    EntryFactory(date=date(2022, 4, 24), athlete=AthleteFactory(strava_id=2))

    actual = Activities.objects.week_stats(pendulum.date(2022, 4, 25))

    assert actual == {1: {"moving_time": 60, "num_activities": 2, "distance": 2, "ascent": 20}}
