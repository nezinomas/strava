import pendulum
from vanilla import ListView, TemplateView

from .lib import utils
from .mixins.views import rendered_content
from .models import Activities
from .services.index import load_service


SORT_BY = ["athlete", "num_activities", "moving_time", "distance", "ascent"]


class Index(TemplateView):
    template_name = "goals/index.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        table_view_kwargs = self.kwargs | {"year": year, "month": month}

        context = {
            "table": rendered_content(self.request, Table, **table_view_kwargs),
            **load_service(year, month).context,
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
