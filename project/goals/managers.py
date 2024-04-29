from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class GoalManager(models.QuerySet):
    def get_goal(self, year, month):
        try:
            return self.get(year=year, month=month)
        except ObjectDoesNotExist:
            return 0


class AthleteManager(models.QuerySet):
    pass


class EntryManager(models.QuerySet):
    pass