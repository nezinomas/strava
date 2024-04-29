import pendulum
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, Sum


class GoalManager(models.QuerySet):
    def get_goal(self, year, month):
        try:
            return self.get(year=year, month=month)
        except ObjectDoesNotExist:
            return 0


class AthleteManager(models.QuerySet):
    pass


class EntryManager(models.QuerySet):
    def related(self):
        return self.select_related("athlete")

    def week_stats(self, date: pendulum.Date):
        start = date.start_of("week")
        end = date.end_of("week")

        qs = (
            self.related()
            .filter(date__gte=start, date__lte=end)
            .annotate(cnt=Count("athlete__strava_id"))
            .values("athlete__strava_id")
            .annotate(
                moving_time=Sum("moving_time"),
                num_activities=Sum("num_activities")
            )
            .order_by("athlete__strava_id")
            .values("athlete__strava_id", "moving_time", "num_activities")
        )

        return {
            entry["athlete__strava_id"]: {
                "moving_time": entry["moving_time"],
                "num_activities": entry["num_activities"],
            }
            for entry in qs
        }
