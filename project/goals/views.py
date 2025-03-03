import pendulum
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from vanilla import ListView, TemplateView
from webob import month

from .forms import GoalForm
from .lib import utils
from .mixins.views import (
    CreateViewMixin,
    DeleteViewMixin,
    UpdateViewMixin,
    rendered_content,
)
from .models import Activities, Goal
from .services.index import load_index_context

SORT_BY = ["athlete", "num_activities", "moving_time", "distance", "ascent"]


class Index(TemplateView):
    template_name = "goals/index.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        table_view_kwargs = self.kwargs | {"year": year, "month": month}

        context = {
            "table": rendered_content(self.request, Table, **table_view_kwargs),
            **load_index_context(year, month),
        }
        return super().get_context_data(**kwargs) | context


class Year(TemplateView):
    template_name = "goals/year.html"

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)

        table_view_kwargs = self.kwargs | {"year": year}

        context = {
            "table": rendered_content(self.request, Table, **table_view_kwargs),
            "year": year,
            "next_year": year + 1,
            "prev_year": year - 1,
        }
        return super().get_context_data(**kwargs) | context


class Table(ListView):
    template_name = "goals/table.html"

    def get_queryset(self):
        order = self.request.GET.get("order")

        year = self.kwargs.get("year")
        month = self.kwargs.get("month")

        period = "month"
        if not month:
            period = "year"
            month = 1

        sql = Activities.objects.activities_stats(pendulum.Date(year, month, 1), period)
        if order and order in SORT_BY:
            sort = order if order == "athlete" else f"-{order}"
            sql = sql.order_by(sort)

        return sql

    def get_context_data(self, **kwargs):
        active_col = self.request.GET.get("order", "moving_time")
        active_col = active_col if active_col in SORT_BY else "moving_time"

        date = str(self.kwargs.get("year"))
        if month := self.kwargs.get("month"):
            date += f" {utils.get_month(month).lower()}"

        context = {
            "date": date,
            "active_col": active_col,
        }
        return super().get_context_data(**kwargs) | context


class Login(auth_views.LoginView):
    template_name = "goals/login.html"
    redirect_authenticated_user = True


class Logout(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.user.is_authenticated:
            logout(request)
            return redirect(reverse("goals:index"))

        return response


class Admin(LoginRequiredMixin, TemplateView):
    template_name = "goals/admin.html"

    def get_context_data(self, **kwargs):
        context = {"goal_list": rendered_content(self.request, GoalList)}
        return super().get_context_data(**kwargs) | context


class GoalList(LoginRequiredMixin, ListView):
    model = Goal

    def get_context_data(self, **kwargs):
        year = pendulum.now().year
        goals_sql = Goal.objects.filter(year=year)
        collected_sql = {
            item["month"]: item["hours"] / 3600
            for item in Activities.objects.year_stats(year)
        }

        object_list = []
        for month_num, month in utils.MONTH_LIST.items():
            goal = goals_sql.filter(month=month_num).first()
            collected = collected_sql.get(month_num)

            css_class = ""
            if goal and collected and month_num <= pendulum.now().month:
                css_class = "goal_success" if collected > goal.hours else "goal_fail"

            object_list.append(
                {
                    "month_num": month_num,
                    "month": month,
                    "goal": goal,
                    "collected": collected,
                    "css_class": css_class,
                }
            )

        context = {
            "object_list": object_list,
        }

        return super().get_context_data(**kwargs) | context


class GoalAdd(LoginRequiredMixin, CreateViewMixin):
    model = Goal
    success_url = reverse_lazy("goals:admin")
    title = "Create Goal"

    def get_form(self, data=None, files=None, **kwargs):
        return GoalForm(data, files, month=self.kwargs.get("month", 1), **kwargs)

    def url(self):
        month = self.kwargs.get("month", 1)
        month = month if 1 <= month <= 12 else 1

        return reverse("goals:goal_add", kwargs={"month": month})


class GoalUpdate(LoginRequiredMixin, UpdateViewMixin):
    model = Goal
    form_class = GoalForm
    success_url = reverse_lazy("goals:admin")
    title = "Update Goal"

    def url(self):
        return self.object.get_absolute_url() if self.object else None


class GoalDelete(LoginRequiredMixin, DeleteViewMixin):
    model = Goal
    success_url = reverse_lazy("goals:goal_list")

    def url(self):
        return self.object.get_delete_url() if self.object else None
