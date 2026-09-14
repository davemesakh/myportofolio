from io import StringIO
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from main.management.commands.import_portfolio_experiences import (
    EXPERIENCES, LEGACY_CALCULUS_DESCRIPTION,
)

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertNotContains(response, '<section class="experience"')
        self.assertContains(response, '<section class="awards"')
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"'
        )

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertNotContains(response, "Present")
        self.assertNotContains(response, 'src=""')
        self.assertContains(
            response,
            f'href="{reverse("main:show_main")}"'
        )

    def test_experience_page_empty_state(self):
        Experience.objects.all().delete()

        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience_status(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        self.experience.refresh_from_db()
        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(self.experience.category, "part-time")



class PortfolioExperienceTest(TestCase):
    def run_import(self, **options):
        output = StringIO()
        call_command("import_portfolio_experiences", stdout=output, **options)
        return output.getvalue()

    def legacy(self):
        return Experience.objects.create(
            title=EXPERIENCES[-1]["title"], description=LEGACY_CALCULUS_DESCRIPTION,
            category="part-time",
        )

    def test_repeat_import_preserves_legacy_identity_and_fields(self):
        legacy = self.legacy()
        original = (legacy.pk, legacy.category, legacy.started_at, legacy.ended_at)
        self.run_import(dry_run=True)
        legacy.refresh_from_db()
        self.assertEqual(Experience.objects.count(), 1)
        self.assertEqual(legacy.description, LEGACY_CALCULUS_DESCRIPTION)
        self.run_import()
        first = list(Experience.objects.order_by("id").values())
        self.assertIn("4 skipped", self.run_import())
        self.assertEqual(first, list(Experience.objects.order_by("id").values()))
        self.assertEqual(Experience.objects.count(), 4)
        legacy.refresh_from_db()
        self.assertEqual((legacy.pk, legacy.category, legacy.started_at, legacy.ended_at), original)
        self.assertEqual(legacy.description, EXPERIENCES[-1]["description"])

    def test_conflict_checks_whole_batch_before_creating(self):
        Experience.objects.create(**{**EXPERIENCES[-1], "description": "Manual edit"})
        with self.assertRaises(CommandError):
            self.run_import()
        self.assertEqual(Experience.objects.count(), 1)

    def test_ambiguous_legacy_is_not_adopted(self):
        self.legacy()
        self.legacy()
        with self.assertRaises(CommandError):
            self.run_import()
        self.assertEqual(Experience.objects.count(), 2)

    def test_unrecognized_legacy_description_is_preserved(self):
        record = self.legacy()
        record.description = "Manual edit"
        record.save()
        with self.assertRaises(CommandError):
            self.run_import()
        record.refresh_from_db()
        self.assertEqual(record.description, "Manual edit")
        self.assertEqual(Experience.objects.count(), 1)

    @patch("main.management.commands.import_portfolio_experiences.finders.find", return_value=None)
    def test_missing_asset_blocks_all_writes(self, finder):
        with self.assertRaises(CommandError):
            self.run_import()
        self.assertFalse(Experience.objects.exists())

    def test_import_is_atomic_on_write_failure(self):
        from django.db.models import QuerySet
        original_create = QuerySet.create
        def fail_second(queryset, **kwargs):
            if kwargs.get("source_key") == EXPERIENCES[1]["source_key"]:
                raise RuntimeError("Simulated failure")
            return original_create(queryset, **kwargs)
        with patch.object(QuerySet, "create", fail_second):
            with self.assertRaises(RuntimeError):
                self.run_import()
        self.assertFalse(Experience.objects.exists())

    def test_unrelated_record_is_untouched(self):
        record = Experience.objects.create(title="Other work", description="Keep this")
        before = Experience.objects.filter(pk=record.pk).values().get()
        self.run_import()
        self.assertEqual(Experience.objects.filter(pk=record.pk).values().get(), before)

    def test_portfolio_content_order_paragraphs_and_periods(self):
        self.run_import()
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        records = list(response.context["experience_list"])
        self.assertEqual([r.source_key for r in records], [d["source_key"] for d in EXPERIENCES])
        self.assertContains(response, 'class="experience-item"', count=4)
        self.assertContains(response, "Present", count=3)
        self.assertContains(response, '<time datetime="2026-04">Apr 2026</time>', html=True)
        self.assertContains(response, '<time datetime="2026-01">Jan 2026</time>', html=True)
        self.assertContains(response, '<time datetime="2026-08">Aug 2026</time>', html=True)
        for data in EXPERIENCES:
            self.assertContains(response, data["title"])
            self.assertContains(response, data["organization"])
            self.assertContains(response, '/static/' + data["logo_static_path"])
            for paragraph in data["description"].split("\n\n"):
                self.assertContains(response, f"<p>{paragraph}</p>", html=True)

    def test_order_tie_uses_id(self):
        import uuid
        for number in (2, 1):
            Experience.objects.create(id=uuid.UUID(int=number), title=str(number), description="x", display_order=1)
        response = self.client.get(reverse("main:show_experience"))
        self.assertEqual([r.title for r in response.context["experience_list"]], ["1", "2"])

    def test_paragraphs_and_autoescaping(self):
        record = Experience.objects.create(title="<script>bad</script>", description="First\r\n \r\n<b>Second</b>")
        self.assertEqual(record.description_paragraphs, ["First", "<b>Second</b>"])
        response = self.client.get(reverse("main:show_experience"))
        self.assertContains(response, "&lt;script&gt;bad&lt;/script&gt;")
        self.assertContains(response, "&lt;b&gt;Second&lt;/b&gt;")
        self.assertNotContains(response, "<script>")

    def test_partial_dates_and_month_validation(self):
        record = Experience(title="Legacy", description="x", start_year=2020)
        self.assertIsNone(record.is_current)
        self.assertEqual(record.start_period, {"iso": "2020", "label": "2020"})
        self.assertIsNone(record.end_period)
        for field in ("start_month", "end_month"):
            for value in (0, 13):
                with self.assertRaises(ValidationError):
                    Experience._meta.get_field(field).clean(value, record)

    def test_completed_period_and_nullable_status(self):
        record = Experience.objects.create(**EXPERIENCES[0])
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, "Present")
        self.assertContains(response, "Apr 2026")
        record.is_current = None
        record.end_year = None
        record.end_month = None
        record.save()
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, "Present")
        self.assertNotContains(response, "None")
