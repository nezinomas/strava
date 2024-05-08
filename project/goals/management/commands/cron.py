from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...lib.writer import Writer
from ...models import Logs


class Command(BaseCommand):
    help = "Get bike activities from Garmin"

    def handle(self, *args, **options):
        try:
            # Writer().write()
            pass
        except Exception as e:
            raise CommandError(f"Can't sync with Strava - {e}")

        Logs.objects.create()

        self.stdout.write(
            self.style.SUCCESS(f"{datetime.now()}: successfully get Strava leaderboard")
        )
