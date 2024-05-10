from datetime import timedelta

import pendulum
from django.urls import reverse
from vanilla import ListView, TemplateView

from .lib import utils
from .mixins.views import rendered_content
from .models import Activities, Goals, Logs


SORT_BY = ["athlete", "num_activities", "moving_time", "distance", "ascent"]


class Index(TemplateView):
    template_name = "goals/index.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        date = pendulum.Date(year, month, 1)

        next_month_int = (date + timedelta(days=32)).month
        previous_month_int = (date - timedelta(days=2)).month

        goal_seconds = Goals.objects.get_goal(year, month)
        goal_hours = goal_seconds / 3600

        collected_seconds = Activities.objects.total_time(date)

        percent = round((collected_seconds * 100 / goal_seconds), 1) if goal_seconds > 0 else 0

        last_update = Logs.objects.filter(status="Success").last()
        last_update = last_update.date if last_update else None

        context = {
            "last_update": last_update,
            "goal_hours": goal_hours,
            "goal_collected": collected_seconds,
            "goal_left": int(goal_seconds - collected_seconds),
            "year": year,
            "month_str": utils.get_month(month),
            "table": rendered_content(self.request, Table, **self.kwargs | {"year": year, "month": month}),
            "chart_data": {
                "categories": ["Tikslas"],
                "target": [goal_hours],
                "fact": [{"y": utils.convert_seconds_to_hours(collected_seconds), "target": goal_hours}],
                "factTitle": "Faktas",
                "targetTitle": "Planas",
                "percent": percent,
                "ymax": goal_hours if int(goal_seconds - collected_seconds) > 0 else None,
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


class Table(ListView):
    template_name = "goals/table.html"

    def get_queryset(self):
        order = self.request.GET.get("order")

        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        sql = Activities.objects.month_stats(pendulum.Date(year, month, 1))
        if order and order in SORT_BY:
            sort = order if order == "athlete" else f"-{order}"
            sql = sql.order_by(sort)

        return sql

    def get_context_data(self, **kwargs):
        active_col = self.request.GET.get("order", "moving_time")
        active_col = active_col if active_col in SORT_BY else "moving_time"

        context = {
            "date": f"{self.kwargs['year']} {utils.get_month(self.kwargs['month']).lower()}",
            "active_col": active_col,

        }
        return super().get_context_data(**kwargs) | context