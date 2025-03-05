from dataclasses import dataclass, field

import polars as pl

from ..lib import utils
from ..models import Activities, Goal


@dataclass
class YearServiceData:
    year: int
    goals: list[dict] = field(init=False, default_factory=list)
    collected: list[dict] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.goals = self.get_goals()
        self.collected = self.get_collected()

    def get_goals(self):
        return [*Goal.objects.filter(year=self.year).values("month", "hours", "pk")]

    def get_collected(self):
        return [*Activities.objects.year_stats(self.year)]


class YearService:
    def __init__(self, data: YearServiceData):
        self._df = self._create_table(data.goals, data.collected)

    @property
    def categories(self):
        return [*utils.MONTH_LIST.values()]

    @property
    def goal_pk(self):
        return self._df["pk"].to_list()

    @property
    def targets(self):
        return self._df["target"].to_list()

    @property
    def collected(self):
        return self._df["y"].to_list()

    @property
    def fact(self):
        return self._df[["target", "y"]].to_dicts()

    @property
    def percent(self):
        return self._df["percent"].to_list()

    @property
    def css_class(self):
        return self._df["color"].to_list()

    def _create_table(self, goals, collected):
        df_goals = self._create_goals_df(goals)
        df_collected = self._create_collected_df(collected)

        return (
            pl.DataFrame({"month": list(range(1, 13))})
            .lazy()
            .join(df_goals, on="month", how="left")
            .join(df_collected, on="month", how="left")
            .fill_null(0)
            .with_columns(percent=(pl.col("y") / pl.col("target") * 100))
            .with_columns(
                color=(
                    pl.when(pl.col("percent") >= 100)
                    .then(pl.lit("goal_success"))
                    .otherwise(pl.lit("goal_fail"))
                )
            )
            .with_columns(
                color=(
                    pl.when(pl.col("target") == 0)
                    .then(pl.lit(""))
                    .otherwise(pl.col("color"))
                )
            )
            .fill_nan(0)
            .sort("month")
        ).collect()

    def _create_goals_df(self, goals):
        if goals:
            return pl.DataFrame(goals).lazy().rename({"hours": "target"})

        return pl.DataFrame(
            {"month": list(range(1, 13)), "target": [0] * 12, "pk": [0] * 12}
        ).lazy()

    def _create_collected_df(self, collected):
        if collected:
            return (
                pl.DataFrame(collected)
                .lazy()
                .rename({"hours": "y"})
                .with_columns(pl.col("y") / 3600)
            )

        return pl.DataFrame({"month": list(range(1, 13)), "y": [0] * 12}).lazy()


def load_year_service(year: int):
    data = YearServiceData(year)
    return YearService(data)
