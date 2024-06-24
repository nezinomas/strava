import pytest
import time_machine
from mock import patch
from pendulum import now

from ..lib.page_parser import Activity, Athlete
from ..lib.writer import Writer
from ..models import Activities, Athletes
from .factories import AthleteFactory, EntryFactory

pytestmark = pytest.mark.django_db


@patch("project.goals.lib.writer.Writer._get_data")
def test_get_data(mck):
    mck.return_value = ("last_week", "this_week")
    last_week, this_week = Writer()._get_data()

    assert last_week == "last_week"
    assert this_week == "this_week"


@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_new_athletes(mck):
    athletes=[Athlete(1, "AAA")]

    assert Athletes.objects.count() == 0

    Writer().new_athletes(athletes)

    actual = Athletes.objects.all()

    assert actual.count() == 1
    assert actual[0].name == "AAA"
    assert actual[0].strava_id == 1


@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_new_athletes_querries(mck, django_assert_max_num_queries):
    athletes=[Athlete(1, "AAA")]

    with django_assert_max_num_queries(2):
        Writer().new_athletes(athletes)


@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_new_athletes_one_exists(mck):
    athletes=[Athlete(2, "AAA")]
    a = AthleteFactory()

    assert Athletes.objects.count() == 1

    Writer().new_athletes(athletes)

    actual = Athletes.objects.all()

    assert actual.count() == 2

    assert actual[0].name == "AAA"
    assert actual[0].strava_id == 2

    assert actual[1].name == a.name
    assert actual[1].strava_id == 1


@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_new_athletes_not_insert(mck):
    AthleteFactory(name="AAA", strava_id=1)
    athletes=[Athlete(1, "AAA")]

    assert Athletes.objects.count() == 1

    Writer().new_athletes(athletes)

    actual = Athletes.objects.all()

    assert actual.count() == 1


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_new(mck):
    AthleteFactory()
    data=[
        Activity(
            strava_id=1,
            moving_time=30,
            distance=1,
            num_activities=1,
            ascent=10,
        )
    ]

    assert Activities.objects.count() == 0

    Writer().new_activities(now(), data)

    actual = Activities.objects.all()

    assert actual.count() == 1


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_moving_time_and_num_activities_exists(mck):
    EntryFactory()
    data=[
        Activity(
            strava_id=1,
            moving_time=30,
            distance=1,
            num_activities=1,
            ascent=10,
        )
    ]

    assert Activities.objects.count() == 1

    Writer().new_activities(now(), data)

    actual = Activities.objects.all()

    assert actual.count() == 1


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_append_new_entry(mck):
    EntryFactory()
    data=[
        Activity(
            strava_id=1,
            moving_time=60,
            distance=2,
            num_activities=2,
            ascent=20,
        )
    ]

    assert Activities.objects.count() == 1

    Writer().new_activities(now(), data)

    actual = Activities.objects.all()

    assert actual.count() == 2

    assert actual[0].moving_time + actual[1].moving_time == 60
    assert actual[0].num_activities + actual[1].num_activities == 2
    assert actual[0].distance + actual[1].distance == 2
    assert actual[0].ascent + actual[1].ascent == 20


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_append_new_entry_num_queries(mck, django_assert_max_num_queries):
    EntryFactory()
    data=[
        Activity(
            strava_id=1,
            moving_time=30,
            distance=1,
            num_activities=2,
            ascent=10,
        )
    ]

    with django_assert_max_num_queries(3):
        Writer().new_activities(now(), data)


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_append_negative_distance(mck):
    EntryFactory(distance=9)
    data=[
        Activity(
            strava_id=1,
            moving_time=60,
            distance=1,
            num_activities=2,
            ascent=10,
        )
    ]

    Writer().new_activities(now(), data)

    actual = Activities.objects.all()

    assert actual.count() == 2
    assert actual[0].distance == 9
    assert actual[1].distance == -8


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_append_negative_ascent(mck):
    EntryFactory(ascent=9)
    data=[
        Activity(
            strava_id=1,
            moving_time=60,
            distance=1,
            num_activities=2,
            ascent=1,
        )
    ]

    Writer().new_activities(now(), data)

    actual = Activities.objects.all()

    assert actual.count() == 2
    assert actual[0].ascent == 9
    assert actual[1].ascent == -8


@time_machine.travel("2022-04-25")
@patch("project.goals.lib.writer.Writer._parse_data", return_value = ([], []))
def test_data_append_negative_num_activities(mck):
    EntryFactory(num_activities=9)
    data=[
        Activity(
            strava_id=1,
            moving_time=60,
            distance=1,
            num_activities=1,
            ascent=1,
        )
    ]

    Writer().new_activities(now(), data)

    actual = Activities.objects.all()

    assert actual.count() == 2
    assert actual[0].num_activities == 9
    assert actual[1].num_activities == -8