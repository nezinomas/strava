import pytest
import time_machine

from project.goals.tests.factories import GoalFactory

from ..forms import GoalForm

pytestmark = pytest.mark.django_db


def test_goal_form():
    GoalForm()


def test_goal_init_fields():
    form = GoalForm().as_p()

    assert '<input type="number" name="year"' in form
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
    assert '<option value="11">Lapkritis</option>' in form
    assert '<option value="12">Gruodis</option>' in form
    assert '<input type="number" name="hours"' in form


@time_machine.travel("2020-11-01")
def test_initial_values():
    form = GoalForm().as_p()

    assert '<input type="number" name="year" value="2020"' in form


@time_machine.travel("2020-11-01")
def test_form_is_not_valid():
    form = GoalForm(data={})

    assert not form.is_valid()
    assert "year" in form.errors
    assert "month" in form.errors
    assert "hours" in form.errors


@time_machine.travel("2020-11-01")
def test_form_is_valid():
    form = GoalForm(data={"year": 2020, "month": 11, "hours": 10})

    assert form.is_valid()


@time_machine.travel("2020-11-01")
def test_form_year_and_month_exist():
    GoalFactory(year=2020, month=11)

    form = GoalForm(data={"year": 2020, "month": 11, "hours": 10})

    assert not form.is_valid()
    assert "Tikslas su šiais Metai ir Mėnuo jau egzistuoja." in form.errors["__all__"]
