from types import SimpleNamespace

import pytest
from mock import patch

from ..lib.page_parser import Athlete
from ..lib.writer import Writer
from ..models import AthleteModel
from .factories import AthleteFactory

pytestmark = pytest.mark.django_db



@patch("project.goals.lib.writer.Writer._get_data")
def test_get_data(mck):
    mck.return_value = ("last_week", "this_week")
    last_week, this_week = Writer()._get_data()

    assert last_week == "last_week"
    assert this_week == "this_week"


@patch("project.goals.lib.writer.Writer._parse_data")
def test_writer_new_athletes(mck):
    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(athletes=[Athlete(1, "AAA")])
    )

    Writer().write()

    actual = AthleteModel.objects.all()

    assert actual.count() == 1
    assert actual[0].name == "AAA"
    assert actual[0].strava_id == 1


@patch("project.goals.lib.writer.Writer._parse_data")
def test_writer_new_athletes_querries(mck, django_assert_num_queries):
    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(athletes=[Athlete(1, "AAA")])
    )

    with django_assert_num_queries(2):
        Writer().write()


@patch("project.goals.lib.writer.Writer._parse_data")
def test_writer_new_athletes_one_exists(mck):
    a = AthleteFactory()

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(athletes=[Athlete(1, "AAA")])
    )

    Writer().write()

    actual = AthleteModel.objects.all()

    assert actual.count() == 2

    assert actual[0].name == "AAA"
    assert actual[0].strava_id == 1

    assert actual[1].name == a.name
    assert actual[1].strava_id == 123456


@patch("project.goals.lib.writer.Writer._parse_data")
def test_writer_new_athletes_not_insert(mck):
    AthleteFactory(name="AAA", strava_id=1)

    mck.return_value = (
        SimpleNamespace(),
        SimpleNamespace(athletes=[Athlete(1, "AAA")])
    )

    Writer().write()

    actual = AthleteModel.objects.all()

    assert actual.count() == 1