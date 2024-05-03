import pytest
import time_machine
from django.urls import resolve, reverse
from pendulum import date

from .. import views
from .factories import EntryFactory

pytestmark = pytest.mark.django_db


def test_index_func():
    view = resolve('/')

    assert views.Index == view.func.view_class


def test_index_year_month_func():
    view = resolve('/1974/1/')

    assert views.Index == view.func.view_class


def test_index_200(client):
    url = reverse('goals:index')
    response = client.get(url)

    assert response.status_code == 200


def test_index_year_month_200(client):
    url = reverse('goals:index_month', kwargs={'year': 1974, 'month': 1})
    response = client.get(url)

    assert response.status_code == 200


def test_index_year_month_records(client):
    EntryFactory()
    EntryFactory(date = date(2022, 5, 1))
    EntryFactory(date = date(2022, 3, 31))

    url = reverse('goals:index_month', kwargs={'year': 2022, 'month': 4})
    response = client.get(url)
    actual = response.context['object_list']

    assert len(actual) == 1
