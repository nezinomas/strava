from datetime import date, datetime, timezone

import pendulum
import pytest
import time_machine

from ..models import Activities, Goal, Logs
from .factories import (
    ActivityFactory,
    AthleteFactory,
    GoalFactory,
    LogFailFactory,
    LogSuccessFactory,
)

pytestmark = pytest.mark.django_db


def test_goal_str():
    goal = GoalFactory()
    assert str(goal) == f"{goal.year} / {goal.month} / {goal.hours}"


def test_goal_current():
    GoalFactory(year=2022, month=2, hours=20)
    GoalFactory(year=2022, month=3, hours=30)
    GoalFactory(year=2022, month=4, hours=40)

    actual = Goal.objects.get_goal(2022, 4)

    assert actual == 144_000  # 40 * 60 * 60


def test_goal_not_set():
    GoalFactory()

    actual = Goal.objects.get_goal(1999, 4)

    assert actual == 0


def test_athlete_str():
    athlete = AthleteFactory()
    assert str(athlete) == athlete.name


def test_activity_str():
    activity = ActivityFactory()
    assert str(activity) == f"{activity.date}: {activity.athlete}"


def test_activity_week_stats():
    ActivityFactory()
    ActivityFactory()
    ActivityFactory(date=date(2022, 4, 24))
    ActivityFactory(date=date(2022, 4, 24), athlete=AthleteFactory(strava_id=2))

    actual = Activities.objects.week_stats(pendulum.date(2022, 4, 25))

    assert actual == {
        1: {"moving_time": 60, "num_activities": 2, "distance": 2, "ascent": 20}
    }


def test_activity_activities_stats_for_month():
    ActivityFactory()
    ActivityFactory()
    ActivityFactory(date=date(2022, 5, 1))

    actual = Activities.objects.activities_stats(pendulum.date(2022, 4, 25))

    assert actual.count() == 1
    assert actual[0]["moving_time"] == 60
    assert actual[0]["num_activities"] == 2
    assert actual[0]["distance"] == 2
    assert actual[0]["ascent"] == 20


def test_activity_activities_stats_for_month_wrong_period():
    ActivityFactory()
    ActivityFactory()
    ActivityFactory(date=date(2022, 5, 1))

    actual = Activities.objects.activities_stats(
        pendulum.date(2022, 4, 25), period="hack"
    )

    assert actual.count() == 1
    assert actual[0]["moving_time"] == 60
    assert actual[0]["num_activities"] == 2
    assert actual[0]["distance"] == 2
    assert actual[0]["ascent"] == 20


def test_activity_activities_stats_for_year():
    ActivityFactory()
    ActivityFactory()
    ActivityFactory(date=date(2023, 5, 1))

    actual = Activities.objects.activities_stats(
        pendulum.date(2022, 1, 25), period="year"
    )

    assert actual.count() == 1
    assert actual[0]["moving_time"] == 60
    assert actual[0]["num_activities"] == 2
    assert actual[0]["distance"] == 2
    assert actual[0]["ascent"] == 20


def test_activity_activities_stats_ordering_by_moving_time():
    a2 = AthleteFactory(strava_id=2)
    a1 = AthleteFactory(strava_id=1)
    ActivityFactory(athlete=a2)
    ActivityFactory(athlete=a1)
    ActivityFactory(athlete=a1)

    actual = Activities.objects.activities_stats(pendulum.date(2022, 4, 25))

    assert actual.count() == 2
    assert actual[0]["athlete_name"] == a1.name
    assert actual[0]["moving_time"] == 60

    assert actual[1]["athlete_name"] == a2.name
    assert actual[1]["moving_time"] == 30


def test_activity_year_stats():
    ActivityFactory(date=date(2022, 4, 25))
    ActivityFactory(date=date(2022, 4, 25))
    ActivityFactory(date=date(2022, 8, 25))
    ActivityFactory(date=date(2022, 8, 25))
    ActivityFactory(date=date(2023, 12, 25))

    actual = Activities.objects.year_stats(year=2022)

    assert actual.count() == 2
    assert actual[0]["hours"] == 60
    assert actual[0]["month"] == 4
    assert actual[1]["hours"] == 60
    assert actual[1]["month"] == 8


def test_activity_total_time():
    ActivityFactory()
    ActivityFactory()
    ActivityFactory(date=date(2022, 5, 1))

    actual = Activities.objects.total_time(pendulum.date(2022, 4, 25))

    assert actual == 60


def test_activity_total_time_no_records():
    actual = Activities.objects.total_time(pendulum.date(2022, 4, 25))

    assert actual == 0


@time_machine.travel("1974-1-2 5:4:3")
def test_log_created():
    Logs.objects.create()

    actual = Logs.objects.last()

    assert actual.date == datetime(1974, 1, 2, 3, 4, 3, tzinfo=timezone.utc)


@time_machine.travel("1974-1-2 5:4:3")
def test_log_successful():
    LogSuccessFactory()

    actual = Logs.objects.last()

    assert actual.date == datetime(1974, 1, 2, 3, 4, 3, tzinfo=timezone.utc)
    assert actual.status == "Success"
    assert not actual.message


@time_machine.travel("1974-1-2 5:4:3")
def test_log_failed():
    LogFailFactory()

    actual = Logs.objects.last()

    assert actual.date == datetime(1974, 1, 2, 3, 4, 3, tzinfo=timezone.utc)
    assert actual.status == "Failed"
    assert actual.message == "Exception message"
