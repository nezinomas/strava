from types import SimpleNamespace

import pytest

from ..services.year import YearService


@pytest.fixture(name="data")
def fixture_data():
    goals = [
        {"month": 1, "hours": 10},
        {"month": 2, "hours": 20},
        {"month": 12, "hours": 120},
    ]

    collected = [
        {"month": 1, "hours": 3_600},
        {"month": 2, "hours": 720_000},
    ]

    return SimpleNamespace(year=2022, goals=goals, collected=collected)


def test_categories(data):
    actual = YearService(data).categories

    assert len(actual) == 12
    assert actual == [
        "Sausis",
        "Vasaris",
        "Kovas",
        "Balandis",
        "Gegužė",
        "Birželis",
        "Liepa",
        "Rugpjūtis",
        "Rugsėjis",
        "Spalis",
        "Lapkritis",
        "Gruodis",
    ]


def test_targets(data):
    actual = YearService(data).targets

    assert len(actual) == 12
    assert actual == [10, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 120]


def test_fact(data):
    actual = YearService(data).fact

    assert len(actual) == 12
    assert actual == [
        {"y": 1.0, "target": 10},
        {"y": 200.0, "target": 20},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 0},
        {"y": 0.0, "target": 120},
    ]


def test_percent(data):
    actual = YearService(data).percent

    assert actual == [10, 1000, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


def test_color(data):
    actual = YearService(data).color

    assert actual == [
        "red",
        "green",
        "neutral",
        "neutral",
        "neutral",
        "neutral",
        "neutral",
        "neutral",
        "neutral",
        "neutral",
        "neutral",
        "red",
    ]
