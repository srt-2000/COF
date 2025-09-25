from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand, OutputWrapper


class Command(BaseCommand):
    help = "Load test-data(to start using coffeeshop site with fully db) from data file on the server"

    def handle(self, *args, **options) -> None:
        self.stdout.write("Loading test-data...")

        try:
            call_command("loaddata", "cof_db.json")
            self.stdout.write(self.style.SUCCESS("Test-data loaded successfully"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"ERROR during loading test-data: {str(e)}"))
