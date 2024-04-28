import pytest

from ..models import Athlete, Entry, Goal
from .factories import AthleteFactory, EntryFactory, GoalFactory

pytestmark = pytest.mark.django_db

def test_goal_str():
    goal = GoalFactory()
    assert str(goal) == f"{goal.year} / {goal.month} / {goal.hours}"

def test_goal_current():
    GoalFactory(year=2022, month=2, hours=20)
    GoalFactory(year=2022, month=3, hours=30)
    GoalFactory(year=2022, month=4, hours=40)

    actual = Goal.objects.get_goal(2022, 4)

    assert actual.hours == 40

def test_goal_not_set():
    GoalFactory()

    actual = Goal.objects.get_goal(1999, 4)

    assert actual == 0


def test_athlete_str():
    athlete = AthleteFactory()
    assert str(athlete) == athlete.name


def test_entry_str():
    entry = EntryFactory()
    assert str(entry) == f"{entry.date}: {entry.athlete}"