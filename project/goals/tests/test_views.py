import datetime

import pytest
import time_machine
from django.urls import resolve, reverse
from pendulum import date

from .. import models, views
from .factories import ActivityFactory, GoalFactory, LogFailFactory, LogSuccessFactory

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
    ActivityFactory()
    ActivityFactory(date=date(2022, 5, 1))
    ActivityFactory(date=date(2022, 3, 31))

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

    ActivityFactory()
    ActivityFactory()
    ActivityFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["chart_data"]

    assert actual["categories"] == ["Tikslas"]
    assert actual["target"] == [10]
    assert actual["fact"][0]["y"] == 0.025
    assert actual["fact"][0]["target"] == 10
    assert actual["factTitle"] == "Faktas"
    assert actual["targetTitle"] == "Planas"
    assert actual["percent"] == 0.2


@time_machine.travel("2022-04-01")
def test_index_collected(client):
    ActivityFactory()
    ActivityFactory()
    ActivityFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["goal_collected"]

    assert actual == 90


@time_machine.travel("2022-04-01")
def test_index_left_to_collect(client):
    GoalFactory(hours=1)

    ActivityFactory()
    ActivityFactory()
    ActivityFactory()

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


def test_index_log_success(client, time_machine):
    time_machine.move_to("1974-1-1 5:4:3")
    LogSuccessFactory()

    time_machine.move_to("2022-04-02")
    LogFailFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["last_update"]

    assert actual == datetime.datetime(
        1974, 1, 1, 3, 4, 3, tzinfo=datetime.timezone.utc
    )


def test_index_log_failed(client, time_machine):
    time_machine.move_to("2022-04-02")
    LogFailFactory()

    url = reverse("goals:index")
    actual = client.get(url).context["last_update"]

    assert not actual


def test_table_view_fuction():
    view = resolve("/table/1974/1/")

    assert views.Table == view.func.view_class


def test_table_view_200(client):
    url = reverse("goals:table", kwargs={"year": 1974, "month": 1})
    response = client.get(url)

    assert response.status_code == 200


def test_login_func():
    view = resolve("/login/")

    assert views.Login == view.func.view_class


def test_successful_login(client, admin_user):
    url = reverse("goals:login")
    credentials = {"username": "admin", "password": "password"}

    response = client.post(url, credentials, follow=True)

    assert response.status_code == 200
    assert response.context["user"].is_authenticated


def test_login_view_form_fields(client):
    url = reverse("goals:login")
    response = client.get(url)

    actual = response.context["form"].fields
    assert "username" in actual
    assert "password" in actual

    actual = response.content.decode("utf-8")
    assert "username" in actual
    assert "password" in actual


def test_login_view_form_errors_no_password(client):
    url = reverse("goals:login")
    response = client.post(url, {"username": "admin", "password": ""})

    assert "Šis laukas yra privalomas." in response.content.decode("utf-8")
    assert "password" in response.context["form"].errors


def test_login_view_form_errors_no_username(client):
    url = reverse("goals:login")
    response = client.post(url, {"username": "", "password": ""})

    assert "Šis laukas yra privalomas." in response.content.decode("utf-8")
    assert "username" in response.context["form"].errors


def test_login_view_wrong_credentials(client):
    url = reverse("goals:login")
    credentials = {"username": "aaaa", "password": "wrong"}

    response = client.post(url, credentials)

    assert not response.context["form"].is_valid()
    assert (
        "Įveskite teisingą vartotojo vardas ir slaptažodį."
        in response.content.decode("utf-8")
    )


def test_redirect_after_successful_login(client, admin_user):
    url = reverse("goals:login")
    credentials = {"username": "admin", "password": "password"}

    response = client.post(url, credentials, follow=True)

    assert response.resolver_match.url_name == "admin"


def test_admin_func():
    view = resolve("/admin/")

    assert views.Admin == view.func.view_class


def test_admin_200(admin_client):
    url = reverse("goals:admin")
    response = admin_client.get(url)

    assert response.status_code == 200


def test_admin_must_be_logged_in(client):
    url = reverse("goals:admin")
    response = client.get(url, follow=True)

    assert response.resolver_match.view_name == "goals:login"


@time_machine.travel("2022-04-01")
def test_admin_context(admin_client):
    url = reverse("goals:admin")
    response = admin_client.get(url)

    assert "object_list" in response.context
    assert len(response.context["object_list"]) == 12


def test_list_func():
    view = resolve("/admin/goal/list/")

    assert views.GoalList is view.func.view_class


def test_list_must_be_logged_in(client):
    url = reverse("goals:goal_list")
    response = client.get(url, follow=True)

    assert response.resolver_match.view_name == "goals:login"


def test_list_200(admin_client):
    url = reverse("goals:goal_list")
    response = admin_client.get(url)

    assert response.status_code == 200


@time_machine.travel("2022-04-01")
def test_list_context_goal(admin_client):
    obj1 = GoalFactory(year=2022, month=1, hours=10)
    obj2 = GoalFactory(year=2022, month=12, hours=120)

    url = reverse("goals:admin")
    response = admin_client.get(url)

    actual = response.context["object_list"]

    assert actual[0]["goal"] == obj1
    assert actual[1]["goal"] is None
    assert actual[2]["goal"] is None
    assert actual[3]["goal"] is None
    assert actual[4]["goal"] is None
    assert actual[5]["goal"] is None
    assert actual[6]["goal"] is None
    assert actual[7]["goal"] is None
    assert actual[8]["goal"] is None
    assert actual[9]["goal"] is None
    assert actual[10]["goal"] is None
    assert actual[11]["goal"] == obj2


@time_machine.travel("2022-04-01")
def test_list_context_css_class(admin_client):
    GoalFactory(year=2022, month=1, hours=10)
    GoalFactory(year=2022, month=2, hours=10)
    GoalFactory(year=2022, month=3, hours=10)
    GoalFactory(year=2022, month=4, hours=10)

    ActivityFactory(date=date(2022, 1, 1), moving_time=1 * 3600)
    ActivityFactory(date=date(2022, 2, 1), moving_time=100 * 3600)
    ActivityFactory(date=date(2022, 4, 1), moving_time=1 * 3600)

    url = reverse("goals:admin")
    response = admin_client.get(url)

    actual = response.context["object_list"]

    assert actual[0]["css_class"] == "goal_fail"
    assert actual[1]["css_class"] == "goal_success"
    assert actual[2]["css_class"] == ""
    assert actual[3]["css_class"] == "goal_fail"


def test_add_func():
    view = resolve("/admin/goal/add/1/")

    assert views.GoalAdd is view.func.view_class


def test_add_must_be_logged_in(client):
    url = reverse("goals:goal_add", kwargs={"month": 1})
    response = client.get(url, follow=True)

    assert response.resolver_match.view_name == "goals:login"


@time_machine.travel("2022-04-01")
def test_add_load_form(admin_client):
    url = reverse("goals:goal_add", kwargs={"month": 11})
    response = admin_client.get(url, {})

    form = response.content.decode("utf-8")

    assert '<input type="number" name="year" value="2022"' in form
    assert '<select name="month"' in form
    assert '<option value="1">Sausis</option>' in form
    assert '<option value="2">Vasaris</option>' in form
    assert '<option value="3">Kovas</option>' in form
    assert '<option value="4">Balandis</option>' in form
    assert '<option value="5">Gegužė</option>' in form
    assert '<option value="6">Birželis</option>' in form
    assert '<option value="7">Liepa</option>' in form
    assert '<option value="8">Rugpjūtis</option>' in form
    assert '<option value="9">Rugsėjis</option>' in form
    assert '<option value="10">Spalis</option>' in form
    assert '<option value="11" selected>Lapkritis</option>' in form
    assert '<option value="12">Gruodis</option>' in form
    assert '<input type="number" name="hours"' in form


@time_machine.travel("2022-04-01")
def test_add_load_form_wrong_month(admin_client):
    url = reverse("goals:goal_add", kwargs={"month": 111})
    response = admin_client.get(url, {})

    form = response.content.decode("utf-8")

    assert f'hx-post="{reverse("goals:goal_add", kwargs={"month": 1})}' in form


def test_add_invalid_data(admin_client):
    url = reverse("goals:goal_add", kwargs={"month": 11})
    data = {}
    form = admin_client.post(url, data).context["form"]

    assert not form.is_valid()
    assert "year" in form.errors
    assert "month" in form.errors
    assert "hours" in form.errors


@time_machine.travel("2022-04-01")
def test_add_save_goal(admin_client):
    url = reverse("goals:goal_add", kwargs={"month": 11})
    data = {"year": 2022, "month": 11, "hours": 222}

    admin_client.post(url, data, follow=True)

    obj = models.Goal.objects.first()

    assert obj.year == 2022
    assert obj.month == 11
    assert obj.hours == 222


def test_update_func():
    view = resolve("/admin/goal/update/1/")

    assert views.GoalUpdate is view.func.view_class


def test_update_must_be_logged_in(client):
    url = reverse("goals:goal_update", kwargs={"pk": 1})
    response = client.get(url, follow=True)

    assert response.resolver_match.view_name == "goals:login"


def test_update(admin_client):
    obj = GoalFactory(year=2022, month=11, hours=222)

    url = reverse("goals:goal_update", kwargs={"pk": obj.pk})
    data = {"year": 2022, "month": 11, "hours": 333}

    admin_client.post(url, data, follow=True)

    obj.refresh_from_db()

    assert obj.year == 2022
    assert obj.month == 11
    assert obj.hours == 333


def test_update_load_form(admin_client):
    obj = GoalFactory()
    url = reverse("goals:goal_update", kwargs={"pk": obj.pk})
    response = admin_client.get(url)

    form = response.content.decode("utf-8")

    assert f' hx-post="{reverse("goals:goal_update", kwargs={"pk": obj.pk})}"' in form
    assert '<input type="number" name="year" value="2022"' in form
    assert '<option value="4" selected>Balandis</option>' in form
    assert '<input type="number" name="hours" value="10"' in form


def test_delete_func():
    view = resolve("/admin/goal/delete/1/")

    assert views.GoalDelete is view.func.view_class


def test_delete_must_be_logged_in(client):
    url = reverse("goals:goal_delete", kwargs={"pk": 1})
    response = client.get(url, follow=True)

    assert response.resolver_match.view_name == "goals:login"


def test_delete_view_200(admin_client):
    obj = GoalFactory()
    url = reverse("goals:goal_delete", kwargs={"pk": obj.pk})
    response = admin_client.get(url)

    assert response.status_code == 200


def test_delete_load_form(admin_client):
    obj = GoalFactory()
    url = reverse("goals:goal_delete", kwargs={"pk": obj.pk})
    response = admin_client.get(url)

    form = response.content.decode("utf-8")

    assert f' hx-post="{reverse("goals:goal_delete", kwargs={"pk": obj.pk})}"' in form
    assert (
        f"Ar tikrai nori ištrinti: <strong>{obj.year} / {obj.month} / "
        f"{obj.hours}</strong>?"
        in form
    )


def test_delete_object_deleted(admin_client):
    obj = GoalFactory()
    assert models.Goal.objects.count() == 1

    url = reverse("goals:goal_delete", kwargs={"pk": obj.pk})
    admin_client.post(url, follow=True)

    assert models.Goal.objects.count() == 0


def test_logout_func():
    view = resolve("/logout/")

    assert views.Logout is view.func.view_class


def test_logout_redirect_to_index(admin_client):
    url = reverse("goals:logout")
    response = admin_client.get(url, follow=True)

    assert response.resolver_match.view_name == "goals:index"
