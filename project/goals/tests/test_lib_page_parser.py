from datetime import datetime

import pytest
from bs4 import BeautifulSoup
import time_machine
from ..lib.page_parser import PageParser


def test_get_items():
    page = """
    <html>
        <body>
            <main>
                <div id="feed-entry-1"></div>
                <div id="feed-entry-2"></div>
            </main>
        </body>
    </html>
    """

    obj = PageParser(page)

    assert len(obj.items) == 2


def test_strava_entry_id():
    item = BeautifulSoup('<div class="------packages-feed-ui-src-features-FeedEntry__entry-container--FPn3K" id="feed-entry-123456789" role="button" style="" tabindex="0"></div>', "html.parser")

    entry_id = PageParser("").get_entry_id(item)
    assert entry_id == 123456789


@pytest.mark.parametrize(
    "value, unit, expected",
    [
        ("12.09", "km", 12090),
        ("2,075", "m", 2),
    ],
)
def test_get_distance(value, unit, expected):
    item = BeautifulSoup(
        f'<li><div class="------packages-ui-Stat-Stat-module__stat--Y2ZBX"><span class="------packages-ui-Stat-Stat-module__statLabel--tiWBB ------packages-feed-ui-src-components-ActivityEntryBody-ActivityEntryBody__stat-label--DjJOy">Distance</span><div class="------packages-ui-Stat-Stat-module__statValue--phtGK">{value}<abbr class="unit" title="kilometers"> {unit}</abbr></div></div></li>',
        "html.parser",
    )

    distance = PageParser("").get_distance(item)
    assert distance == expected


def test_get_distance_not_found():
    item = BeautifulSoup("<li></li>", "html.parser")

    distance = PageParser("").get_distance(item)
    assert distance == 0


def test_get_time_minutes_seconds():
    item = BeautifulSoup(
        '<div class="------packages-ui-Stat-Stat-module__stat--Y2ZBX"><span class="------packages-ui-Stat-Stat-module__statLabel--tiWBB ------packages-feed-ui-src-components-ActivityEntryBody-ActivityEntryBody__stat-label--DjJOy">Time</span><div class="------packages-ui-Stat-Stat-module__statValue--phtGK">1<abbr class="unit" title="minute">m</abbr> 2<abbr class="unit" title="second">s</abbr></div></div>',
        "html.parser",
    )

    time = PageParser("").get_time(item)
    assert time == 62


def test_get_time_hours_minutes():
    item = BeautifulSoup(
        '<div class="------packages-ui-Stat-Stat-module__stat--Y2ZBX"><span class="------packages-ui-Stat-Stat-module__statLabel--tiWBB ------packages-feed-ui-src-components-ActivityEntryBody-ActivityEntryBody__stat-label--DjJOy">Time</span><div class="------packages-ui-Stat-Stat-module__statValue--phtGK">1<abbr class="unit" title="hour">h</abbr> 2<abbr class="unit" title="minute">m</abbr></div></div>',
        "html.parser",
    )

    time = PageParser("").get_time(item)
    assert time == 3720


def test_get_activity():
    item = BeautifulSoup(
        '<div class="------packages-feed-ui-src-features-Activity-Activity__entry-icon--hn2AC"><svg fill="currentColor" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" class="------packages-feed-ui-src-features-Activity-Activity__activity-icon--lq3sA"><title>Walk</title><g fill=""><path d="M8.33"></path></g></svg></div>',
        "html.parser",
    )

    activity = PageParser("").get_activity(item)
    assert activity == "Walk"


def test_get_ascent():
    item = BeautifulSoup(
        '<div class="------packages-ui-Stat-Stat-module__stat--Y2ZBX"><span class="------packages-ui-Stat-Stat-module__statLabel--tiWBB ------packages-feed-ui-src-components-ActivityEntryBody-ActivityEntryBody__stat-label--DjJOy">Elev Gain</span><div class="------packages-ui-Stat-Stat-module__statValue--phtGK">68<abbr class="unit" title="meters"> m</abbr></div></div>',
        "html.parser",
    )

    ascent = PageParser("").get_ascent(item)
    assert ascent == 68


def test_get_strava_id():
    item = BeautifulSoup(
        '<div class="------packages-feed-ui-src-components-HeaderWithOwnerMetadata-HeaderWithOwnerMetadata-module__nameBoosted--ejkqR"><a href="/athletes/5577666" data-testid="owners-name">UserName</a></div>',
        "html.parser",
    )

    strava_id = PageParser("").get_strava_id(item)
    assert strava_id == 5577666


def test_get_name():
    item = BeautifulSoup(
        '<div class="------packages-feed-ui-src-components-HeaderWithOwnerMetadata-HeaderWithOwnerMetadata-module__nameBoosted--ejkqR"><a href="/athletes/5577666" data-testid="owners-name">UserName</a></div>',
        "html.parser",
    )

    name = PageParser("").get_name(item)
    assert name == "UserName"


@pytest.mark.parametrize(
    "value, expect",
    [
        ("21 April 2024", datetime(2024, 4, 21, 0, 0, 0)),
        ("21 April 2024 at 15:00", datetime(2024, 4, 21, 15, 0, 0)),
        ("April 21, 2024", datetime(2024, 4, 21, 0, 0, 0)),
        ("April 21 2024", datetime(2024, 4, 21, 0, 0, 0)),
        ("April 21, 2024 at 06:05 AM", datetime(2024, 4, 21, 6, 5, 0)),
        ("April 21, 2024 at 06:05 PM", datetime(2024, 4, 21, 18, 5, 0)),
        ("April 21, 2024 at 06:05", datetime(2024, 4, 21, 6, 5, 0)),
        ("April 21, 2024 at 18:05", datetime(2024, 4, 21, 18, 5, 0)),
        ("Today", datetime(2022, 4, 25, 0, 0, 0)),
        ("Today at 6:36 AM", datetime(2022, 4, 25, 6, 36, 0)),
        ("Today at 6:36 PM", datetime(2022, 4, 25, 18, 36, 0)),
        ("Yesterday", datetime(2022, 4, 24, 0, 0, 0)),
        ("Yesterday at 6:36 AM", datetime(2022, 4, 24, 6, 36, 0)),
        ("Yesterday at 6:36 PM", datetime(2022, 4, 24, 18, 36, 0)),
    ],
)
@time_machine.travel("2022-04-25")
def test_get_date(value, expect):
    item = BeautifulSoup(
        f'<time data-testid="date_at_time">{value}</time>', "html.parser"
    )

    date = PageParser("").get_date(item)

    assert date == expect
