from dataclasses import asdict

import pendulum

from ..models import AthleteModel, EntryModel
from .page_getter import (get_last_week_leaderboard_html, get_leaderboard,
                          get_leaderboard_html)
from .page_parser import PageParser


class Writer:

    def __init__(self):
        self.last_week, self.this_week = self._parse_data()

    def _get_data(self):
        html = get_leaderboard()

        return get_last_week_leaderboard_html(html), get_leaderboard_html(html)

    def _parse_data(self):
        last_week, this_week = self._get_data()

        return PageParser(last_week), PageParser(this_week)

    def new_athletes(self):
        athletes = self.this_week.athletes
        atheletes_db = AthleteModel.objects.all().values_list("strava_id", flat=True)

        if data := [
            AthleteModel(**asdict(athlete))
            for athlete in athletes
            if athlete.strava_id not in atheletes_db
        ]:
            AthleteModel.objects.bulk_create(data)

    def new_data(self):
        entries = self.this_week.data
        week_data = EntryModel.objects.week_stats(pendulum.today())
        data = []
        for entry in entries:
            athlete = AthleteModel.objects.get(strava_id=entry.strava_id)
            entry_db = week_data.get(entry.strava_id)
            if not entry_db or (
                entry_db.get("moving_time", 0) < entry.moving_time
                or entry_db.get("num_activities", 0) < entry.num_activities
            ):
                data.append(
                    EntryModel(
                        athlete=athlete,
                        date=pendulum.today(),
                        moving_time=entry.moving_time,
                        distance=entry.distance,
                        ascent=entry.ascent,
                    )
                )

        if data:
            EntryModel.objects.bulk_create(data)

    def write(self):
        self.new_athletes()
        self.new_data()
