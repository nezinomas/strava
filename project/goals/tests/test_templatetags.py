import pytest
from django.template import Context, Template


@pytest.fixture(name="seconds_template")
def fixture_seconds_template():
    return Template("{% load filters %}{{ val|convert_seconds }}")


@pytest.fixture(name="meters_template")
def fixture_meters_template():
    return Template("{% load filters %}{{ val|convert_meters }}")


@pytest.mark.parametrize(
    "value, expect",
    [
        (3600, "1h 0m"),
        (60, "1m"),
        (5400, "1h 30m"),
    ],
)
def test_convert_seconds(value, expect, seconds_template):
    context = Context({"val": value})

    actual =  seconds_template.render(context)

    assert actual == expect


@pytest.mark.parametrize(
    "value, expect",
    [
        (1100, "1,1km"),
        (100, '0,1km'),
    ],
)
def test_convert_meters(value, expect, meters_template):
    context = Context({"val": value})

    actual =  meters_template.render(context)

    assert actual == expect


@pytest.mark.parametrize(
    "value, expect",
    [
        ("John Smith", "John Sm."),
        ("John Smith-Doe", "John Sm."),
    ],
)
def test_cut_name(value, expect):
    context = Context({"val": value})
    template = Template("{% load filters %}{{ val|cut_name }}")

    actual = template.render(context)

    assert actual == expect