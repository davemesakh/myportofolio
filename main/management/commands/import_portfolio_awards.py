from html import unescape

from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from main.models import Award


# Snapshot of the two original Awards articles in templates/index.html.
AWARDS = (
    {
        "source_key": "osnk-physics-2024",
        "title": unescape("OSN-K &mdash; Physics"),
        "achievement": unescape("3rd Place &middot; City Level"),
        "year": 2024,
        "description": "Awarded third place in Physics at the city-level Olimpiade Sains Nasional (OSN-K) in 2024.",
        "photo_static_path": "img/award-osnk-2024.jpeg",
        "photo_alt": "Indoor group photo at the 2024 OSN-K event",
        "photo_width": 1280,
        "photo_height": 960,
        "display_order": 1,
    },
    {
        "source_key": "fls2n-singing-2023",
        "title": unescape("FLS2N &mdash; Male Solo Singing"),
        "achievement": unescape("3rd Place &middot; East Jakarta City Level"),
        "year": 2023,
        "description": "Awarded third place in the Male Solo Singing category at the East Jakarta city-level Festival dan Lomba Seni Siswa Nasional (FLS2N) in 2023.",
        "photo_static_path": "img/award-fls2n-2023.jpeg",
        "photo_alt": "David holding a trophy on stage alongside other award recipients at FLS2N 2023",
        "photo_width": 768,
        "photo_height": 1024,
        "display_order": 2,
    },
)


class Command(BaseCommand):
    help = "Import the two original portfolio awards without overwriting existing data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true", help="Check and show the plan without writing data."
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        with transaction.atomic():
            conflicts = []
            to_create = []
            skipped = 0
            for data in AWARDS:
                key = data["source_key"]
                path = data["photo_static_path"]
                if finders.find(path):
                    self.stdout.write(f"ASSET OK: {path}")
                else:
                    conflicts.append(f"Missing static asset: {path}")

                candidates = Award.objects.filter(
                    Q(source_key__isnull=True) | Q(source_key=""),
                    title=data["title"],
                    year=data["year"],
                )
                if candidates.exists():
                    conflicts.append(f"{key}: matching title/year exists without source_key")

                existing = Award.objects.filter(source_key=key).first()
                if existing is None:
                    to_create.append(data)
                    self.stdout.write(f"PLAN CREATE: {key}")
                else:
                    differences = [
                        field for field, value in data.items()
                        if getattr(existing, field) != value
                    ]
                    if differences:
                        conflicts.append(f"{key}: different fields: {', '.join(differences)}")
                    else:
                        skipped += 1
                        self.stdout.write(f"PLAN SKIP: {key} (identical)")

            # Validate the entire batch before the first write.
            if conflicts:
                raise CommandError("Import blocked; no data written:\n" + "\n".join(conflicts))

            if dry_run:
                self.stdout.write(
                    f"DRY RUN: {len(to_create)} to create, {skipped} to skip; no data written."
                )
                return

            for data in to_create:
                Award.objects.create(**data)
            self.stdout.write(
                self.style.SUCCESS(f"Created {len(to_create)} awards; skipped {skipped}.")
            )
