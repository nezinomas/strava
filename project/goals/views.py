import pendulum
from vanilla import ListView

from project.goals.models import Activities, Goals


class Index(ListView):
    template_name = "goals/index.html"
    model = Activities

    def get_queryset(self):
        return Activities.objects.month_stats(pendulum.now().date())

    def get_context_data(self, **kwargs):
        year = self.kwargs.get("year", pendulum.now().year)
        month = self.kwargs.get("month", pendulum.now().month)

        goal = Goals.objects.get_goal(year, month)
        collected = Activities.objects.total_time(pendulum.Date(year, month, 1))

        context = {
            "goal_hours": goal / 3600,
            "goal_collected": collected,
            "goal_left": goal - collected,
            "year": year,
            "month": month
        }
        return super().get_context_data(**kwargs) | context