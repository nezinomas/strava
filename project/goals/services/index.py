from dataclasses import dataclass, field
from datetime import date, timedelta

import pendulum
from django.urls import reverse

from ..lib import utils
from ..models import Activities, Goals, Logs


@dataclass
class IndexServiceData:
    year: int
    month: int
    goal: int = field(init=False, default=0)
    collected: int = field(init=False, default=0)
    last_update: date = field(init=False, default=None)

    def __post_init__(self):
        self.goal = self.get_goal()
        self.collected = self.get_collected()
        self.last_update = self.get_last_update()

    def get_goal(self):
        return Goals.objects.get_goal(self.year, self.month)

    def get_collected(self):
        return Activities.objects.total_time(pendulum.Date(self.year, self.month, 1))

    def get_last_update(self):
        return Logs.objects.filter(status="Success").last()


class IndexService:
    def __init__(self, year: int, month: int, data: IndexServiceData):
        self.year = year
        self.month = month
        self.date = pendulum.Date(year, month, 1)

        self.goal = data.goal
        self.goal_hours = self.goal / 3600

        self.collected = data.collected

        self.last_update = data.last_update.date if data.last_update else None

    @property
    def percent(self):
        return round((self.collected * 100 / self.goal), 1) if self.goal > 0 else 0

    @property
    def next_month(self):
        next_month_int = (self.date + timedelta(days=32)).month
        return {
            "url": reverse(
                "goals:index_month",
                kwargs={
                    "year": (self.year + 1) if self.month == 12 else self.year,
                    "month": next_month_int,
                },
            ),
            "title": utils.get_month(next_month_int),
        }

    @property
    def previous_month(self):
        previous_month_int = (self.date - timedelta(days=2)).month
        return {
            "url": reverse(
                "goals:index_month",
                kwargs={
                    "year": (self.year - 1) if self.month == 1 else self.year,
                    "month": previous_month_int,
                },
            ),
            "title": utils.get_month(previous_month_int),
        }

    @property
    def left_to_collect(self):
        return int(self.goal - self.collected)

    @property
    def chart_context(self):
        return {
            "categories": ["Tikslas"],
            "target": [self.goal_hours],
            "fact": [
                {
                    "y": utils.convert_seconds_to_hours(self.collected),
                    "target": self.goal_hours,
                }
            ],
            "factTitle": "Faktas",
            "targetTitle": "Planas",
            "percent": self.percent,
            "ymax": self.goal_hours if int(self.goal - self.collected) > 0 else None,
        }

    @property
    def context(self):
        return {
            "year": self.year,
            "month_str": utils.get_month(self.month),
            "last_update": self.last_update,
            "goal_hours": self.goal_hours,
            "goal_collected": self.collected,
            "goal_left": self.left_to_collect,
            "chart_data": self.chart_context,
            "next": self.next_month,
            "previous": self.previous_month,
        }


def load_service(year, month):
    data = IndexServiceData(year, month)

    return IndexService(year, month, data)
