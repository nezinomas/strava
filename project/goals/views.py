from datetime import timedelta

import pendulum
from django.urls import reverse
from vanilla import ListView, TemplateView

from .lib import utils
from .mixins.views import rendered_content
from .models import Activities, Goals, Logs


class Index(TemplateView):
    template_name = "goals/index.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        date = pendulum.Date(year, month, 1)

        next_month_int = (date + timedelta(days=32)).month
        previous_month_int = (date - timedelta(days=2)).month

        goal = Goals.objects.get_goal(year, month) / 3600
        collected = Activities.objects.total_time(date)

        last_update = Logs.objects.last()
        last_update = last_update.date + timedelta(hours=3) if last_update else None

        context = {
            "last_update": last_update,
            "goal_hours": goal,
            "goal_collected": collected,
            "goal_left": int(goal * 3600 - collected),
            "year": year,
            "month_str": utils.get_month(month),
            "table": rendered_content(self.request, Table, **self.kwargs | {"year": year, "month": month}),
            "chart_data": {
                "categories": ["Tikslas"],
                "target": [goal],
                "fact": [{"y": utils.convert_seconds_to_hours(collected), "target": goal}],
                "factTitle": "Faktas",
                "targetTitle": "Planas",
                "ymax": goal if int(goal * 3600 - collected) > 0 else None,
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
        if order and order in ["athlete", "num_activities", "moving_time", "distance", "ascent"]:
            sort = order if order == "athlete" else f"-{order}"
            sql = sql.order_by(sort)

        return sql

    def get_context_data(self, **kwargs):
        active_col = self.request.GET.get("order") or "moving_time"

        context = {
            "date": f"{self.kwargs['year']} {utils.get_month(self.kwargs['month']).lower()}",
            "active_col": active_col,

        }
        return super().get_context_data(**kwargs) | context