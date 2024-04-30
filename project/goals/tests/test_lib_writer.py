from types import SimpleNamespace

import pytest
import time_machine
from mock import patch

from ..lib.page_parser import Athlete, Activity
from ..lib.writer import Writer
from ..models import Athletes, Activities
from .factories import AthleteFactory, EntryFactory

pytestmark = pytest.mark.django_db


@patch("project.goals.lib.writer.Writer._get_data")
def test_get_data(mck):
    mck.return_value = ("last_week", "this_week")
    last_week, this_week = Writer()._get_data()

    assert last_week == "last_week"
    assert this_week == "this_week"


@patch("project.goals.lib.writer.Writer._parse_data")
def test_new_athletes(mck):
    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(1, "AAA")],
            data=[],
        ),
    )
    assert Athletes.objects.count() == 0

    Writer().new_athletes()

    actual = Athletes.objects.all()

    assert actual.count() == 1
    assert actual[0].name == "AAA"
    assert actual[0].strava_id == 1


@patch("project.goals.lib.writer.Writer._parse_data")
def test_new_athletes_querries(mck, django_assert_num_queries):
    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(1, "AAA")],
            data=[],
        ),
    )

    with django_assert_num_queries(2):
        Writer().new_athletes()


@patch("project.goals.lib.writer.Writer._parse_data")
def test_new_athletes_one_exists(mck):
    a = AthleteFactory()

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(2, "AAA")],
            data=[],
        ),
    )

    assert Athletes.objects.count() == 1

    Writer().new_athletes()

    actual = Athletes.objects.all()

    assert actual.count() == 2

    assert actual[0].name == "AAA"
    assert actual[0].strava_id == 2

    assert actual[1].name == a.name
    assert actual[1].strava_id == 1


@patch("project.goals.lib.writer.Writer._parse_data")
def test_new_athletes_not_insert(mck):
    AthleteFactory(name="AAA", strava_id=1)

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(1, "AAA")],
            data=[],
        ),
    )

    assert Athletes.objects.count() == 1

    Writer().new_athletes()

    actual = Athletes.objects.all()

    assert actual.count() == 1

@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data")
def test_data_new(mck):
    AthleteFactory()

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(strava_id=1, name="AAA")],
            data=[
                Activity(
                    strava_id=1,
                    moving_time=30,
                    distance=1,
                    num_activities=1,
                    ascent=10,
                )
            ],
        ),
    )

    assert Activities.objects.count() == 0

    Writer().new_data()

    actual = Activities.objects.all()

    assert actual.count() == 1


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data")
def test_data_moving_time_and_num_activities_exists(mck):
    EntryFactory()

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(strava_id=1, name="AAA")],
            data=[
                Activity(
                    strava_id=1,
                    moving_time=30,
                    distance=1,
                    num_activities=1,
                    ascent=10,
                )
            ],
        ),
    )

    assert Activities.objects.count() == 1

    Writer().new_data()

    actual = Activities.objects.all()

    assert actual.count() == 1


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data")
def test_data_append_new_entry(mck):
    EntryFactory()

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(strava_id=1, name="AAA")],
            data=[
                Activity(
                    strava_id=1,
                    moving_time=30,
                    distance=1,
                    num_activities=2,
                    ascent=10,
                )
            ],
        ),
    )

    assert Activities.objects.count() == 1

    Writer().new_data()

    actual = Activities.objects.all()

    assert actual.count() == 2

@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data")
def test_data_append_new_entry_num_queries(mck, django_assert_num_queries):
    EntryFactory()

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(
            athletes=[Athlete(strava_id=1, name="AAA")],
            data=[
                Activity(
                    strava_id=1,
                    moving_time=30,
                    distance=1,
                    num_activities=2,
                    ascent=10,
                )
            ],
        ),
    )

    with django_assert_num_queries(3):
        Writer().new_data()