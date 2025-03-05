import pendulum
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from vanilla import ListView, TemplateView

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
from .services.year import load_year_service

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
        o = load_year_service(year)

        table_view_kwargs = self.kwargs | {"year": year}

        load_year_service(year)

        context = {
            "table": rendered_content(self.request, Table, **table_view_kwargs),
            "year": year,
            "next_year": year + 1,
            "prev_year": year - 1,
            "chart_data": {
                "categories": o.categories,
                "targets": o.targets,
                "fact": o.fact,
                "percent": o.percent,
                "css_class": o.css_class,
            }
        }
        return super().get_context_data(**kwargs) | context


class Table(ListView):
    template_name = "goals/table.html"

    def get_queryset(self):
        year = self.kwargs.get("year")
        month = self.kwargs.get("month")
        order = self.request.GET.get("order")
        period = "month" if month else "year"

        sql = Activities.objects.activities_stats(
            date=pendulum.Date(year, month or 1, 1), period=period
        )

        if order and order in SORT_BY:
            sort = order if order == "athlete" else f"-{order}"
            sql = sql.order_by(sort)

        return sql

    def get_context_data(self, **kwargs):
        active_col = self.request.GET.get("order", "moving_time")
        active_col = active_col if active_col in SORT_BY else "moving_time"

        msg = str(self.kwargs.get("year"))
        if month := self.kwargs.get("month"):
            msg += f" {utils.get_month(month).lower()}"

        context = {
            "msg": msg,
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
        obj = load_year_service(year)

        context = {
            "objects": zip(
                obj.categories, obj.goal_pk, obj.targets, obj.collected, obj.css_class
            )
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
