from dataclasses import asdict
from datetime import timedelta

import pendulum

from ..models import Activities, Athletes
from .page_getter import (
    get_last_week_leaderboard_html,
    get_leaderboard,
    get_leaderboard_html,
)
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

    def new_athletes(self, athletes):
        atheletes_db = Athletes.objects.all().values_list("strava_id", flat=True)

        if data := [
            Athletes(**asdict(athlete))
            for athlete in athletes
            if athlete.strava_id not in atheletes_db
        ]:
            Athletes.objects.bulk_create(data)

    def new_activities(self, dt: pendulum.DateTime, activities: list):
        week_data = Activities.objects.week_stats(dt)
        data = []
        for entry in activities:
            entry_db = week_data.get(entry.strava_id)

            num_activities = 0
            moving_time = 0
            distance = 0
            ascent = 0

            if entry_db:
                num_activities = entry_db["num_activities"]
                moving_time = entry_db["moving_time"]
                distance = entry_db["distance"]
                ascent = entry_db["ascent"]

                if (
                    moving_time >= entry.moving_time
                    or num_activities >= entry.num_activities
                ):
                    continue

            athlete = Athletes.objects.get(strava_id=entry.strava_id)
            data.append(
                Activities(
                    athlete=athlete,
                    date=dt,
                    num_activities=entry.num_activities - num_activities,
                    moving_time=entry.moving_time - moving_time,
                    distance=entry.distance - distance,
                    ascent=entry.ascent - ascent,
                )
            )

        if data:
            Activities.objects.bulk_create(data)

    def write(self):
        # this week
        dt = pendulum.now("Europe/Vilnius")
        self.new_athletes(self.this_week.athletes)
        self.new_activities(dt, self.this_week.data)

        # last week
        dt = dt.start_of("week") - timedelta(hours=1)
        self.new_athletes(self.last_week.athletes)
        self.new_activities(dt, self.last_week.data)
