from dataclasses import asdict

from ..models import AthleteModel
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

        data = [
            AthleteModel(**asdict(athlete))
            for athlete in athletes
            if athlete.strava_id not in atheletes_db
        ]
        AthleteModel.objects.bulk_create(data)

    def write(self):
        self.new_athletes()