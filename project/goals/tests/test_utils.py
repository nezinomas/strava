import pytest

from ..lib import utils


@pytest.mark.parametrize(
    "value, expect",
    [
        (60, (0, 1)),
        (3600, (1, 0)),
        (3660, (1, 1)),
    ],
)
def test_convert_seconds(value, expect):
    actual = utils.convert_seconds(value)
    assert actual == expect


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
