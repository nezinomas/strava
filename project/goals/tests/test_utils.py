import pytest

from ..lib import utils


@pytest.mark.parametrize(
    "value, expect",
    [
        (60, (0, 1, 0)),
        (3600, (1, 0, 0)),
        (3660, (1, 1, 0)),
        (3661, (1, 1, 1)),
    ],
)
def test_convert_seconds(value, expect):
    actual = utils.convert_seconds(value)
    assert actual == expect


@pytest.mark.parametrize(
    "value, expect",
    [
        (60, 0.02),
        (3600, 1),
        (5400, 1.5),
    ],
)
def test_convert_seconds_to_hours(value, expect):
    actual = utils.convert_seconds_to_hours(value)
    assert round(actual, 2) == expect


@pytest.mark.parametrize(
    "value, expect",
    [
        (1, "Sausis"),
        (13, "Sausis"),
    ],
)
def test_get_month(value, expect):
    actual = utils.get_month(value)
    assert actual == expect
