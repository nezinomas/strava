from datetime import timedelta

import pendulum
from django.urls import reverse
from vanilla import ListView

from .lib import utils
from .models import Activities, Goals


class Index(ListView):
    template_name = "goals/index.html"
    model = Activities

    def get_queryset(self):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        return Activities.objects.month_stats(pendulum.Date(year, month, 1))

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        date = pendulum.Date(year, month, 1)

        next_month_int = (date + timedelta(days=32)).month
        previous_month_int = (date - timedelta(days=2)).month

        goal = Goals.objects.get_goal(year, month)
        collected = Activities.objects.total_time(date)

        context = {
            "goal_hours": goal / 3600,
            "goal_collected": collected,
            "goal_left": goal - collected,
            "year": year,
            "month_int": month,
            "month_str": utils.get_month(month),
            "chart_data": {
                "categories": ["Tikslas"],
                "target": [goal / 3600],
                "fact": [{"y": utils.convert_seconds_to_hours(collected), "target": goal / 3600}],
                "factTitle": "Faktas",
                "targetTitle": "Planas",
            },
            "next": {
                "url": reverse("goals:index_month", kwargs={"year": (year + 1) if month == 12 else year, "month": next_month_int}),
                "title": utils.get_month(next_month_int),
            },
            "previous": {
                "url": reverse("goals:index_month", kwargs={"year": (year - 1) if month == 1 else year, "month": previous_month_int}),
                "title": utils.get_month(previous_month_int),
            }
        }
        return super().get_context_data(**kwargs) | context