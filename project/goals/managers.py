import pendulum
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, F, Sum
from django.db.models.functions import ExtractMonth, TruncMonth


class GoalManager(models.QuerySet):
    def get_goal(self, year, month):
        try:
            return self.get(year=year, month=month).hours * 3600
        except ObjectDoesNotExist:
            return 0


class AthleteManager(models.QuerySet):
    pass


class ActivityManager(models.QuerySet):
    def related(self):
        return self.select_related("athlete")

    def week_stats(self, date: pendulum.Date):
        start = date.start_of("week")
        end = date.end_of("week")

        qs = (
            self.related()
            .filter(date__range=[start, end])
            .annotate(cnt=Count("athlete__strava_id"))
            .values("athlete__strava_id")
            .annotate(
                num_activities=Sum("num_activities"),
                moving_time=Sum("moving_time"),
                distance=Sum("distance"),
                ascent=Sum("ascent"),
            )
            .order_by("athlete__strava_id")
            .values(
                "athlete__strava_id",
                "moving_time",
                "num_activities",
                "distance",
                "ascent",
            )
        )

        return {
            entry["athlete__strava_id"]: {
                "num_activities": entry["num_activities"],
                "moving_time": entry["moving_time"],
                "distance": entry["distance"],
                "ascent": entry["ascent"],
            }
            for entry in qs
        }

    def activities_stats(self, date: pendulum.Date, period: str = "month"):
        if period not in ["month", "year"]:
            period = "month"

        start = date.start_of(period)
        end = date.end_of(period)

        return (
            self.related()
            .filter(date__range=[start, end])
            .annotate(cnt=Count("athlete__strava_id"))
            .values("athlete__strava_id")
            .annotate(
                num_activities=Sum("num_activities"),
                moving_time=Sum("moving_time"),
                distance=Sum("distance"),
                ascent=Sum("ascent"),
            )
            .order_by("athlete__strava_id")
            .values(
                "moving_time",
                "num_activities",
                "distance",
                "ascent",
                athlete_name=F("athlete__name"),
            )
            .order_by("-moving_time")
        )

    def year_stats(self, year: int):
        return (
            self.related()
            .filter(date__year=year)
            .annotate(cnt=Count("id"))
            .values("id")
            .annotate(date_trunc=TruncMonth("date"))
            .values("date_trunc")
            .annotate(hours=Sum("moving_time"))
            .order_by("date_trunc")
            .values("hours", month=ExtractMonth("date_trunc"))
        )

    def total_time(self, date: pendulum.Date):
        start = date.start_of("month")
        end = date.end_of("month")

        return (
            self.related()
            .filter(date__range=[start, end])
            .aggregate(Sum("moving_time"))
            .get("moving_time__sum")
            or 0
        )
