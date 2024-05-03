import pytest
import time_machine
from django.urls import resolve, reverse
from pendulum import date

from .. import views
from .factories import EntryFactory, GoalFactory

pytestmark = pytest.mark.django_db


def test_index_func():
    view = resolve("/")

    assert views.Index == view.func.view_class


def test_index_year_month_func():
    view = resolve("/1974/1/")

    assert views.Index == view.func.view_class


def test_index_200(client):
    url = reverse("goals:index")
    response = client.get(url)

    assert response.status_code == 200


def test_index_year_month_200(client):
    url = reverse("goals:index_month", kwargs={"year": 1974, "month": 1})
    response = client.get(url)

    assert response.status_code == 200


def test_index_year_month_records(client):
    EntryFactory()
    EntryFactory(date=date(2022, 5, 1))
    EntryFactory(date=date(2022, 3, 31))

    url = reverse("goals:index_month", kwargs={"year": 2022, "month": 4})
    response = client.get(url)
    actual = response.context["object_list"]

    assert len(actual) == 1


@time_machine.travel("1974-01-01")
def test_index_next_prev_links_january(client):
    url = reverse("goals:index")
    actual = client.get(url).context

    _next = actual["next"]
    _prev = actual["previous"]
    assert _next["url"] == reverse(
        "goals:index_month", kwargs={"year": 1974, "month": 2}
    )
    assert _next["title"] == "Vasaris"

    assert _prev["url"] == reverse(
        "goals:index_month", kwargs={"year": 1973, "month": 12}
    )
    assert _prev["title"] == "Gruodis"


@time_machine.travel("1974-12-01")
def test_index_next_prev_links_december(client):
    url = reverse("goals:index")
    actual = client.get(url).context

    _next = actual["next"]
    _prev = actual["previous"]
    assert _next["url"] == reverse(
        "goals:index_month", kwargs={"year": 1975, "month": 1}
    )
    assert _next["title"] == "Sausis"

    assert _prev["url"] == reverse(
        "goals:index_month", kwargs={"year": 1974, "month": 11}
    )
    assert _prev["title"] == "Lapkritis"


@time_machine.travel("2022-04-01")
def test_index_goal_hours(client):
    GoalFactory()

    url = reverse("goals:index")
    actual = client.get(url).context

    assert actual["goal_hours"] == 10


@time_machine.travel("2022-04-01")
def test_index_chart_data(client):
    GoalFactory()

    EntryFactory()
    EntryFactory()
    EntryFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["chart_data"]

    assert actual["categories"] == ["Tikslas"]
    assert actual["target"] == [10]
    assert actual["fact"][0]["y"] == 0.025
    assert actual["fact"][0]["target"] == 10
    assert actual["factTitle"] == "Faktas"
    assert actual["targetTitle"] == "Planas"


@time_machine.travel("2022-04-01")
def test_index_collected(client):
    EntryFactory()
    EntryFactory()
    EntryFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["goal_collected"]

    assert actual == 90


@time_machine.travel("2022-04-01")
def test_index_left_to_collect(client):
    GoalFactory(hours=1)

    EntryFactory()
    EntryFactory()
    EntryFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["goal_left"]

    assert actual == 3_510


@time_machine.travel("2022-04-01")
def test_index_month_str(client):
    url = reverse("goals:index")
    actual = client.get(url).context["month_str"]

    assert actual == "Balandis"


@time_machine.travel("2022-04-01")
def test_index_year(client):
    url = reverse("goals:index")
    actual = client.get(url).context["year"]

    assert actual == 2022
