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
        for activity in activities:
            db_activity = week_data.get(activity.strava_id, {})

            db_num_activity = db_activity.get("num_activities", 0)
            db_moving_time = db_activity.get("moving_time", 0)
            db_distance = db_activity.get("distance", 0)
            db_ascent = db_activity.get("ascent", 0)

            if db_moving_time >= activity.moving_time or db_num_activity >= activity.num_activities:
                continue

            athlete = Athletes.objects.get(strava_id=activity.strava_id)
            data.append(
                Activities(
                    athlete=athlete,
                    date=dt,
                    num_activities=activity.num_activities - db_num_activity,
                    moving_time=activity.moving_time - db_moving_time,
                    distance=activity.distance - db_distance,
                    ascent=activity.ascent - db_ascent,
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
