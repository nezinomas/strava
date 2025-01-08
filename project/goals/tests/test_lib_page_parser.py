import pytest
from bs4 import BeautifulSoup

from ..lib.page_parser import Activity, Athlete, PageParser


@pytest.fixture(name="table_html")
def fixture_table_html():
    return """
    <div class="leaderboard">
        <table  class="dense striped sortable">
            <thead>
                <tr><th></th></tr>
            </thead>
            <tbody>
                <tr>
                    <td class="athlete">
                        <a class="athlete-name minimalt" href="/athletes/123456789">AAA A.</a>
                    </td>

                    <td class="moving_time">
                        1<abbr class="unit" title="minute">m</abbr>
                    </td>

                    <td class="num_activities">1</td>

                    <td class="distance">1 <abbr class="unit short" title="kilometers">km</abbr></td>

                    <td class="elev_gain">100 <abbr class="unit short" title="meters">m</abbr></td>
                </tr>
            </tbody>
        </table>
    </div>
    """


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


def test_num_activities():
    item = BeautifulSoup(
        '<td class="num_activities">666</td>',
        "html.parser",
    )

    distance = PageParser("").get_num_activities(item)
    assert distance == 666


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


@pytest.mark.parametrize(
    "value, expect",
    [
        ("117", 117),
        ("117,1", 117),
        ("2,091", 2091),
    ],
)
def test_get_ascent(value, expect):
    item = BeautifulSoup(
        f'<td class="elev_gain">{value} <abbr class="unit short" title="meters">m</abbr></td>',
        "html.parser",
    )

    ascent = PageParser("").get_ascent(item)
    assert ascent == expect


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


def test_athletes_list(table_html):
    obj = PageParser(table_html)

    assert len(obj.athletes) == 1
    assert obj.athletes[0] == Athlete(strava_id=123456789, name="AAA A.")


def test_data_list(table_html):
    obj = PageParser(table_html)

    assert len(obj.data) == 1
    assert obj.data[0] == Activity(
        strava_id=123456789, moving_time=60, distance=1000, num_activities=1, ascent=100
    )
