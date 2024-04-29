import pytest
from bs4 import BeautifulSoup

from ..lib.page_parser import PageParser


def test_get_items():
    page = """
    <div class="leaderboard">
        <table  class="dense striped sortable">
            <thead>
                <tr><th></th></tr>
            </thead>
            <tbody>
                <tr><td></td></tr>
                <tr><td></td></tr>
            </tbody>
        </table>
    </div>
    """

    obj = PageParser(page)

    assert len(obj.items) == 2


@pytest.mark.parametrize(
    "value, expect",
    [
        ("0.6", 600),
        ("1.6", 1600),
    ],
)
def test_get_distance(value, expect):
    item = BeautifulSoup(
        f'<td class="distance">{value} <abbr class="unit short" title="kilometers">km</abbr></td>',
        "html.parser",
    )

    distance = PageParser("").get_distance(item)
    assert distance == expect


def test_get_distance_empty():
    item = BeautifulSoup(
        '<td class="distance">--</td>',
        "html.parser",
    )

    distance = PageParser("").get_distance(item)
    assert distance == 0


def test_get_time_minutes():
    item = BeautifulSoup(
        '<td class="moving_time highlighted-column">1<abbr class="unit" title="minute">m</abbr></td>',
        "html.parser",
    )

    time = PageParser("").get_time(item)
    assert time == 60


def test_get_time_hours_minutes():
    item = BeautifulSoup(
        '<td class="moving_time highlighted-column">1<abbr class="unit" title="hour">h</abbr> 2<abbr class="unit" title="minute">m</abbr></td>',
        "html.parser",
    )

    time = PageParser("").get_time(item)
    assert time == 3720


def test_get_ascent():
    item = BeautifulSoup(
        '<td class="elev_gain">117 <abbr class="unit short" title="meters">m</abbr></td>',
        "html.parser",
    )

    ascent = PageParser("").get_ascent(item)
    assert ascent == 117


def test_get_ascent_empty():
    item = BeautifulSoup(
        '<td class="elev_gain">--</td>',
        "html.parser",
    )

    ascent = PageParser("").get_ascent(item)
    assert ascent == 0


def test_get_strava_id():
    item = BeautifulSoup(
        '<a class="athlete-name minimal" href="/athletes/123456789">UserName</a>',
        "html.parser",
    )

    strava_id = PageParser("").get_strava_id(item)
    assert strava_id == 123456789


def test_get_name():
    item = BeautifulSoup(
        '<a class="athlete-name minimal" href="/athletes/123456789">UserName</a>',
        "html.parser",
    )

    name = PageParser("").get_name(item)
    assert name == "UserName"
