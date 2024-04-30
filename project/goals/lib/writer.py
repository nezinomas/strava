from dataclasses import asdict
from datetime import timedelta

import pendulum

from ..models import Athletes, Activities
from .page_getter import (get_last_week_leaderboard_html, get_leaderboard,
                          get_leaderboard_html)
from .page_parser import PageParser


class Writer:

    def __init__(self):
        self.last_week, self.this_week = self._parse_data()

    def _get_data(self):
        html = get_leaderboard()

        this_week = get_leaderboard_html(html)
        last_week = get_last_week_leaderboard_html(html)

        return last_week, this_week

    def _parse_data(self):
        last_week, this_week = self._get_data()

        return PageParser(last_week), PageParser(this_week)

    def new_athletes(self, athletes=None):
        if not athletes:
            athletes = self.this_week.athletes

        atheletes_db = Athletes.objects.all().values_list("strava_id", flat=True)

        if data := [
            Athletes(**asdict(athlete))
            for athlete in athletes
            if athlete.strava_id not in atheletes_db
        ]:
            Athletes.objects.bulk_create(data)

    def new_data(self, dt=None, entries=None):
        if not dt:
            dt = pendulum.now('Europe/Vilnius')

        if not entries:
            entries = self.this_week.data

        week_data = Activities.objects.week_stats(dt)
        data = []
        for entry in entries:
            entry_db = week_data.get(entry.strava_id)

            if not entry_db or (
                entry_db.get("moving_time", 0) < entry.moving_time
                or entry_db.get("num_activities", 0) < entry.num_activities
            ):
                athlete = Athletes.objects.get(strava_id=entry.strava_id)
                data.append(
                    Activities(
                        athlete=athlete,
                        date=dt,
                        moving_time=entry.moving_time,
                        distance=entry.distance,
                        ascent=entry.ascent,
                    )
                )

        if data:
            Activities.objects.bulk_create(data)

    def write(self):
        # this week
        self.new_athletes()
        self.new_data()

        # last week
        dt = pendulum.now('Europe/Vilnius').start_of("week") - timedelta(hours=1)
        self.new_athletes(self.last_week.athletes)
        self.new_data(dt, self.last_week.data)
