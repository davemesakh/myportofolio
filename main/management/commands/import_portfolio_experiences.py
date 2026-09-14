from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from main.models import Experience


# Snapshot of the original Profile Experience section, preserving paragraph boundaries.
EXPERIENCES = ({'source_key': 'betis-teacher-2026',
  'title': 'Quantitative Knowledge Teacher',
  'organization': 'BETIS Fasilkom UI',
  'description': 'Taught and mentored over 60 students in the Quantitative Knowledge (Pengetahuan '
                 'Kuantitatif) section of the SNBT university entrance exam. Developed mathematics '
                 'curricula and practice modules, simplifying algebra, geometry, and logic to help '
                 'students solve problems more quickly and accurately.\n'
                 '\n'
                 'Led intensive weekly learning sessions and evaluations, helping students improve '
                 'their mock-test performance and academic readiness.',
  'logo_static_path': 'img/logo-betis-2026.jpg',
  'logo_alt': 'BETIS Fasilkom UI logo',
  'start_year': 2026,
  'start_month': 1,
  'end_year': 2026,
  'end_month': 4,
  'is_current': False,
  'display_order': 1},
 {'source_key': 'compfest-academy-2026',
  'title': 'Software Engineer Academy Staff',
  'organization': 'COMPFEST Fasilkom UI',
  'description': 'Recruited and coordinated mentors, speakers, and judges for the Software '
                 'Engineer Academy program. Assessed participant assignments and conducted '
                 'interviews as part of the selection process.\n'
                 '\n'
                 'Served as master of ceremonies during program sessions and events.',
  'logo_static_path': 'img/logo-compfest.jpg',
  'logo_alt': 'COMPFEST Fasilkom UI logo',
  'start_year': 2026,
  'start_month': 4,
  'end_year': None,
  'end_month': None,
  'is_current': True,
  'display_order': 2},
 {'source_key': 'ddpo-hr-2026',
  'title': 'HR Staff',
  'organization': 'DDP0 Arung, Fasilkom UI',
  'description': 'Support recruitment, onboarding, and welfare coordination for staff and mentors '
                 'of the DDP0 introductory programming initiative, helping maintain smooth '
                 'communication.',
  'logo_static_path': 'img/logo-ddpo-arung.jpg',
  'logo_alt': 'DDP0 Arung, Fasilkom UI logo',
  'start_year': 2026,
  'start_month': 4,
  'end_year': None,
  'end_month': None,
  'is_current': True,
  'display_order': 3},
 {'source_key': 'calculus-ta-2026',
  'title': 'Teaching Assistant, Calculus 1',
  'organization': 'Fasilkom UI',
  'description': 'Assist with delivering course material, holding tutorial sessions, and grading '
                 'assignments for first-year Calculus 1 students.',
  'logo_static_path': 'img/logo-fasilkom-ui.png',
  'logo_alt': 'Fasilkom UI logo',
  'start_year': 2026,
  'start_month': 8,
  'end_year': None,
  'end_month': None,
  'is_current': True,
  'display_order': 4})


LEGACY_CALCULUS_DESCRIPTION = (
    "Assist with delivering course material, tutorial sessions, and grading assignments "
    "for first-year Calculus 1 students."
)


class Command(BaseCommand):
    help = "Import original portfolio experiences; reconcile the known legacy Calculus record."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Inspect without writing data.")

    def handle(self, *args, **options):
        with transaction.atomic():
            conflicts, plans = [], []
            skipped = 0
            for data in EXPERIENCES:
                key = data["source_key"]
                if not finders.find(data["logo_static_path"]):
                    conflicts.append(f"{key}: missing logo {data['logo_static_path']}")
                else:
                    self.stdout.write(f"ASSET OK: {data['logo_static_path']}")
                existing = Experience.objects.select_for_update().filter(source_key=key).first()
                candidates = list(Experience.objects.select_for_update().filter(
                    Q(source_key__isnull=True) | Q(source_key=""), title=data["title"]
                ))
                if existing:
                    if candidates:
                        conflicts.append(f"{key}: additional unkeyed candidate(s)")
                    changed = [field for field, value in data.items() if getattr(existing, field) != value]
                    if changed:
                        conflicts.append(f"{key}: different fields: {', '.join(changed)}")
                    else:
                        skipped += 1
                        self.stdout.write(f"SKIP: {key} (identical)")
                elif candidates:
                    if key != "calculus-ta-2026" or len(candidates) != 1:
                        conflicts.append(f"{key}: unkeyed matching is ambiguous or unauthorized")
                        continue
                    candidate = candidates[0]
                    # Only adopt the known legacy shape; never replace populated manual fields.
                    allowed_descriptions = (LEGACY_CALCULUS_DESCRIPTION, data["description"])
                    changes = [field for field, value in data.items()
                               if field not in ("source_key", "description", "title")
                               and getattr(candidate, field) not in (None, "")
                               and not (field == "display_order" and candidate.display_order == 0)
                               and getattr(candidate, field) != value]
                    if candidate.description not in allowed_descriptions or changes:
                        conflicts.append(f"{key}: legacy data differs; manual reconciliation required")
                        continue
                    plans.append((candidate, data))
                    self.stdout.write(f"PLAN RECONCILE: {key}; preserve ID {candidate.pk}, category and timestamps")
                    self.stdout.write(f"Description before: {candidate.description}")
                    self.stdout.write(f"Description after: {data['description']}")
                else:
                    plans.append((None, data))
                    self.stdout.write(f"PLAN CREATE: {key}")
            if conflicts:
                raise CommandError("Import blocked; no data written:\n" + "\n".join(conflicts))
            creates = sum(record is None for record, _ in plans)
            updates = len(plans) - creates
            if options["dry_run"]:
                self.stdout.write(f"DRY RUN: {creates} create, {updates} reconcile, {skipped} skip; no writes")
                return
            for record, data in plans:
                if record is None:
                    # The source provides no category; retain the model's existing default.
                    Experience.objects.create(**data)
                else:
                    for field, value in data.items():
                        setattr(record, field, value)
                    record.save(update_fields=list(data))
            self.stdout.write(self.style.SUCCESS(
                f"Imported: {creates} created, {updates} reconciled, {skipped} skipped"
            ))
