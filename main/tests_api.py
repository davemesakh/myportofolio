import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience
from main.serializers import ExperienceSerializer


class ExperienceAPITest(APITestCase):
    owner_password = "Test-only-API-password-2026"
    response_fields = {
        "id", "title", "description", "category", "organization",
        "logo_static_path", "logo_alt", "start_year", "start_month",
        "end_year", "end_month", "is_current", "display_order",
        "star_count", "is_starred", "description_paragraphs",
        "start_period", "end_period", "logo_url",
    }

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", email="owner@example.com", password=self.owner_password
        )
        self.visitor = User.objects.create_user(username="visitor")
        self.editor = User.objects.create_user(username="editor")
        self.editor.groups.add(Group.objects.create(name="Editor"))
        self.staff = User.objects.create_user(
            username="staff", is_staff=True, is_superuser=False
        )
        self.payload = {
            "title": "Data Analyst Intern",
            "description": "Built dashboards.\n\nAnalyzed operational data.",
            "category": "research",
            "organization": "Example Studio",
            "logo_static_path": "img/logo-fasilkom-ui.png",
            "logo_alt": "Example logo",
            "start_year": 2025,
            "start_month": 6,
            "end_year": 2026,
            "end_month": 1,
            "is_current": False,
            "display_order": 2,
        }
        self.experience = Experience.objects.create(
            id=uuid.UUID(int=2), source_key="api-fixture", **self.payload
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse(
            "api:experience-detail", args=[self.experience.pk]
        )
        self.star_url = reverse("api:experience-star", args=[self.experience.pk])

    def database_state(self):
        return (
            list(Experience.objects.order_by("id").values()),
            list(
                Experience.starred_by.through.objects.order_by(
                    "experience_id", "user_id"
                ).values_list("experience_id", "user_id")
            ),
        )

    def assert_validation_error(self, response, field):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(field, response.data)
        self.assertIsInstance(response.data[field], list)
        self.assertTrue(response.data[field])
        self.assertTrue(all(isinstance(error, str) for error in response.data[field]))

    def assert_crud_writes_denied(self):
        before = self.database_state()
        for method, url, payload in (
            ("post", self.list_url, self.payload),
            ("put", self.detail_url, self.payload),
            ("patch", self.detail_url, {"title": "Unauthorized update"}),
            ("delete", self.detail_url, {}),
        ):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertIn("detail", response.data)
                self.assertEqual(self.database_state(), before)

    def test_guest_can_list_direct_array_without_legacy_nesting(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        record = response.data[0]
        self.assertEqual(record["id"], str(self.experience.pk))
        self.assertEqual(record["title"], self.payload["title"])
        self.assertEqual(set(record), self.response_fields)
        self.assertIs(record["is_starred"], False)
        self.assertEqual(record["star_count"], 0)
        self.assertNotIn("fields", record)

    def test_guest_can_retrieve_detail_and_display_fields(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.experience.pk))
        self.assertEqual(set(response.data), self.response_fields)
        self.assertEqual(
            response.data["description_paragraphs"],
            ["Built dashboards.", "Analyzed operational data."],
        )
        self.assertEqual(response.data["start_period"], {
            "iso": "2025-06", "label": "Jun 2025",
        })
        self.assertEqual(response.data["end_period"], {
            "iso": "2026-01", "label": "Jan 2026",
        })
        self.assertEqual(response.data["logo_url"], "/static/img/logo-fasilkom-ui.png")
        self.assertIs(response.data["is_starred"], False)

    def test_public_head_and_options_allow_safe_access(self):
        for url in (self.list_url, self.detail_url):
            with self.subTest(url=url):
                response = self.client.head(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.content, b"")
                response = self.client.options(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIn("name", response.data)
                self.assertIn("HEAD", response["Allow"])
                self.assertIn("OPTIONS", response["Allow"])

    def test_list_orders_by_display_order_then_uuid(self):
        tied = Experience.objects.create(
            id=uuid.UUID(int=1), **(self.payload | {"title": "Tied"})
        )
        earlier = Experience.objects.create(
            id=uuid.UUID(int=3), **(self.payload | {"display_order": 1})
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [record["id"] for record in response.data],
            [str(earlier.pk), str(tied.pk), str(self.experience.pk)],
        )

    def test_search_matches_title_organization_and_category_without_writes(self):
        other = Experience.objects.create(
            title="Other Role", description="Other description", category="volunteer"
        )
        before = self.database_state()
        for query in ("aNaLySt", "  ANALYST  ", "STUDIO", "SEARCH"):
            with self.subTest(query=query):
                response = self.client.get(self.list_url, {"title": query})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    [record["id"] for record in response.data],
                    [str(self.experience.pk)],
                )
        for query in ("", "   "):
            with self.subTest(query=query):
                response = self.client.get(self.list_url, {"title": query})
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(
                    {record["id"] for record in response.data},
                    {str(self.experience.pk), str(other.pk)},
                )
        self.assertEqual(self.database_state(), before)

    def test_search_without_matches_returns_empty_array(self):
        before = self.database_state()

        response = self.client.get(self.list_url, {"title": "no-such-experience"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
        self.assertEqual(self.database_state(), before)

    def test_unknown_uuid_returns_404_without_creating_or_modifying_records(self):
        missing_id = uuid.uuid4()
        detail_url = reverse("api:experience-detail", args=[missing_id])
        star_url = reverse("api:experience-star", args=[missing_id])
        before = self.database_state()
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.client.force_authenticate(user=self.owner)
        for method, url, payload in (
            ("put", detail_url, self.payload),
            ("patch", detail_url, {"title": "Missing"}),
            ("delete", detail_url, {}),
            ("post", star_url, {}),
        ):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                self.assertIn("detail", response.data)
                self.assertEqual(self.database_state(), before)

    def test_guest_cannot_write_or_star(self):
        self.assert_crud_writes_denied()
        before = self.database_state()

        response = self.client.post(self.star_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(self.database_state(), before)

    def test_regular_user_can_read_but_cannot_write_experiences(self):
        self.client.force_authenticate(user=self.visitor)
        self.assert_crud_writes_denied()
        for url in (self.list_url, self.detail_url):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                record = response.data[0] if url == self.list_url else response.data
                self.assertEqual(record["id"], str(self.experience.pk))

    def test_editor_can_read_and_update_with_put_and_patch(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.experience.pk))

        response = self.client.put(
            self.detail_url, self.payload | {"title": "Editor PUT"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Editor PUT")
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Editor PUT")

        response = self.client.patch(
            self.detail_url, {"organization": "Editor PATCH"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["organization"], "Editor PATCH")
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.organization, "Editor PATCH")
        self.assertEqual(self.experience.title, "Editor PUT")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        before = self.database_state()
        for method, url in (("post", self.list_url), ("delete", self.detail_url)):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, self.payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertIn("detail", response.data)
                self.assertEqual(self.database_state(), before)

    def test_superuser_can_create_experience(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=uuid.UUID(response.data["id"]))
        self.assertNotEqual(created.pk, self.experience.pk)
        for field, value in self.payload.items():
            self.assertEqual(getattr(created, field), value)
            self.assertEqual(response.data[field], value)
        self.assertEqual(Experience.objects.count(), 2)
        self.assertEqual(response.data["star_count"], 0)
        self.assertIs(response.data["is_starred"], False)

    def test_superuser_can_read_and_update_with_put_and_patch(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.experience.pk))
        response = self.client.put(
            self.detail_url, self.payload | {"title": "Owner PUT"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Owner PUT")
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Owner PUT")
        response = self.client.patch(
            self.detail_url, {"title": "Owner PATCH"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Owner PATCH")
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Owner PATCH")

    def test_superuser_delete_returns_empty_204_and_preserves_other_records(self):
        other = Experience.objects.create(title="Keep", description="Keep this record")
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertIsNone(response.data)
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertTrue(Experience.objects.filter(pk=other.pk).exists())
        self.assertFalse(self.visitor.starred_experiences.exists())

    def test_staff_status_alone_does_not_grant_crud_write_access(self):
        self.assertTrue(self.staff.is_staff)
        self.assertFalse(self.staff.is_superuser)
        self.assertFalse(self.staff.groups.filter(name="Editor").exists())
        self.client.force_authenticate(user=self.staff)
        self.assert_crud_writes_denied()

    def test_invalid_create_payloads_return_field_errors_without_writes(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_state()
        cases = (
            ({"title": "   "}, "title"),
            ({"title": "<b></b>"}, "title"),
            ({"description": "<em></em>"}, "description"),
            ({"logo_static_path": "javascript:alert(1)"}, "logo_static_path"),
            ({"logo_static_path": "http://example.com/logo.png"}, "logo_static_path"),
            ({"logo_static_path": "data:image/png;base64,AAAA"}, "logo_static_path"),
            ({"logo_static_path": "../img/logo.png"}, "logo_static_path"),
            ({"start_year": None}, "start_month"),
            ({"end_year": None}, "end_month"),
            ({"end_year": 2024}, "non_field_errors"),
            ({"end_year": 2025, "end_month": 5}, "non_field_errors"),
            ({"is_current": True}, "is_current"),
            ({"category": "invalid-category"}, "category"),
            ({"title": "x" * 256}, "title"),
            ({"start_month": 0}, "start_month"),
            ({"end_month": 13}, "end_month"),
            ({"display_order": -1}, "display_order"),
        )
        for changes, field in cases:
            with self.subTest(changes=changes):
                response = self.client.post(
                    self.list_url, self.payload | changes, format="json"
                )
                self.assert_validation_error(response, field)
                self.assertEqual(self.database_state(), before)

    def test_create_cleans_text_and_preserves_supported_logo_sources(self):
        self.client.force_authenticate(user=self.owner)
        sources = (
            ("img/logo.png", "/static/img/logo.png"),
            ("https://example.com/logo.png", "https://example.com/logo.png"),
            (
                "https://drive.google.com/file/d/FILE_ID/view?usp=sharing",
                "https://drive.google.com/thumbnail?id=FILE_ID&sz=w512",
            ),
        )
        for source, resolved in sources:
            with self.subTest(source=source):
                payload = self.payload | {
                    "title": "  <b>Clean title</b>  ",
                    "description": "  <b>First</b>\n\nSecond  ",
                    "organization": "  <b>Clean organization</b>  ",
                    "logo_alt": "  <em>Clean logo</em>  ",
                    "logo_static_path": source,
                }
                response = self.client.post(self.list_url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                record = Experience.objects.get(pk=response.data["id"])
                for field, expected in (
                    ("title", "Clean title"),
                    ("description", "First\n\nSecond"),
                    ("organization", "Clean organization"),
                    ("logo_alt", "Clean logo"),
                    ("logo_static_path", source),
                ):
                    self.assertEqual(getattr(record, field), expected)
                    self.assertEqual(response.data[field], expected)
                self.assertEqual(response.data["logo_url"], resolved)

    def test_create_preserves_nullable_status_and_partial_dates(self):
        self.client.force_authenticate(user=self.owner)
        payload = self.payload | {
            "start_month": None, "end_year": None,
            "end_month": None, "is_current": None,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        for field in ("start_month", "end_year", "end_month", "is_current"):
            self.assertIsNone(getattr(created, field))
            self.assertIsNone(response.data[field])
        self.assertEqual(response.data["start_period"], {"iso": "2025", "label": "2025"})
        self.assertIsNone(response.data["end_period"])

    def test_patch_changes_only_submitted_fields(self):
        self.client.force_authenticate(user=self.editor)
        before = Experience.objects.values().get(pk=self.experience.pk)

        response = self.client.patch(
            self.detail_url, {"title": "Only title changes"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Only title changes")
        self.assertEqual(
            Experience.objects.values().get(pk=self.experience.pk),
            before | {"title": "Only title changes"},
        )

    def test_patch_validates_retained_dates_and_preserves_invalid_state(self):
        self.client.force_authenticate(user=self.editor)
        before = self.database_state()
        for changes, field in (
            ({"end_year": 2024}, "non_field_errors"),
            ({"end_year": 2025, "end_month": 5}, "non_field_errors"),
            ({"start_year": None}, "start_month"),
            ({"end_year": None}, "end_month"),
        ):
            with self.subTest(changes=changes):
                response = self.client.patch(self.detail_url, changes, format="json")
                self.assert_validation_error(response, field)
                self.assertEqual(self.database_state(), before)

    def test_patch_current_requires_explicitly_clearing_existing_end_period(self):
        self.client.force_authenticate(user=self.editor)
        before = self.database_state()
        response = self.client.patch(
            self.detail_url, {"is_current": True}, format="json"
        )
        self.assert_validation_error(response, "is_current")
        self.assertEqual(self.database_state(), before)

        response = self.client.patch(self.detail_url, {
            "is_current": True, "end_year": None, "end_month": None,
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertIs(self.experience.is_current, True)
        self.assertIsNone(self.experience.end_year)
        self.assertIsNone(self.experience.end_month)
        self.assertEqual(self.experience.start_year, 2025)
        self.assertIs(response.data["is_current"], True)
        self.assertIsNone(response.data["end_period"])

    def test_put_requires_title_and_description_and_preserves_invalid_data(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_state()
        for payload, field in (
            ({"title": "No description"}, "description"),
            ({"description": "No title"}, "title"),
        ):
            with self.subTest(field=field):
                response = self.client.put(self.detail_url, payload, format="json")
                self.assert_validation_error(response, field)
                self.assertEqual(self.database_state(), before)

        response = self.client.put(self.detail_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        for field, value in self.payload.items():
            self.assertEqual(getattr(self.experience, field), value)
            self.assertEqual(response.data[field], value)

    def test_regular_user_can_toggle_own_star_without_affecting_other_users(self):
        self.experience.starred_by.add(self.editor)
        self.client.force_authenticate(user=self.visitor)

        response = self.client.post(self.star_url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["is_starred"], True)
        self.assertEqual(response.data["star_count"], 2)
        self.assertTrue(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
        response = self.client.post(self.star_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["is_starred"], False)
        self.assertEqual(response.data["star_count"], 1)
        self.assertFalse(self.experience.starred_by.filter(pk=self.visitor.pk).exists())
        self.assertTrue(self.experience.starred_by.filter(pk=self.editor.pk).exists())

    def test_editor_and_superuser_can_toggle_stars(self):
        for user in (self.editor, self.owner):
            with self.subTest(user=user.username):
                self.client.force_authenticate(user=user)
                response = self.client.post(self.star_url, format="json")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIs(response.data["is_starred"], True)
                self.assertEqual(response.data["star_count"], 1)
                self.assertEqual(list(self.experience.starred_by.all()), [user])
                response = self.client.post(self.star_url, format="json")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertIs(response.data["is_starred"], False)
                self.assertEqual(response.data["star_count"], 0)
                self.assertFalse(self.experience.starred_by.exists())

    def test_star_state_is_specific_to_the_current_viewer(self):
        self.experience.starred_by.add(self.visitor)
        for user, expected in ((self.visitor, True), (self.editor, False), (None, False)):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                for url in (self.list_url, self.detail_url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    record = response.data[0] if url == self.list_url else response.data
                    self.assertIs(record["is_starred"], expected)
                    self.assertEqual(record["star_count"], 1)

    def test_client_cannot_control_star_fields_or_expose_user_identities(self):
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.owner)
        before = self.database_state()

        response = self.client.patch(self.detail_url, {
            "star_count": 999,
            "is_starred": True,
            "starred_by": [self.owner.pk],
            "starred_by_names": ["injected-name"],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["star_count"], 1)
        self.assertIs(response.data["is_starred"], False)
        self.assertEqual(set(response.data), self.response_fields)
        self.assertEqual(self.database_state(), before)
        for private_field in ("starred_by", "starred_by_names", "username", "email", "password"):
            self.assertNotIn(private_field, response.data)
        self.assertNotIn(self.owner.email, response.content.decode())
        self.assertNotIn("injected-name", response.content.decode())

    def test_uuid_timestamps_and_import_key_cannot_be_changed(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_state()

        response = self.client.patch(self.detail_url, {
            "id": str(uuid.uuid4()),
            "started_at": "2000-01-01T00:00:00Z",
            "ended_at": "2001-01-01T00:00:00Z",
            "source_key": "client-controlled",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.experience.pk))
        self.assertEqual(self.database_state(), before)
        for field in ("started_at", "ended_at", "source_key"):
            self.assertNotIn(field, response.data)

    def test_unsupported_methods_return_405_for_authorized_requesters(self):
        self.client.force_authenticate(user=self.owner)
        before = self.database_state()
        for method, url in (
            ("delete", self.list_url), ("put", self.list_url),
            ("patch", self.list_url), ("post", self.detail_url),
            ("get", self.star_url), ("put", self.star_url),
            ("patch", self.star_url), ("delete", self.star_url),
        ):
            with self.subTest(method=method, url=url):
                response = getattr(self.client, method)(url, {}, format="json")
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
                self.assertIn("detail", response.data)
                self.assertEqual(self.database_state(), before)

    def test_real_session_without_csrf_rejects_all_unsafe_operations(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password=self.owner_password))
        self.assertEqual(int(client.session["_auth_user_id"]), self.owner.pk)
        before = self.database_state()

        for method, url, payload in (
            ("post", self.list_url, self.payload),
            ("put", self.detail_url, self.payload),
            ("patch", self.detail_url, {"title": "Without CSRF"}),
            ("delete", self.detail_url, {}),
            ("post", self.star_url, {}),
        ):
            with self.subTest(method=method, url=url):
                response = getattr(client, method)(url, payload, format="json")
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertIn("CSRF", str(response.data["detail"]))
                self.assertEqual(self.database_state(), before)

    def test_real_session_browsable_api_cookie_allows_csrf_protected_create(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password=self.owner_password))
        self.assertEqual(int(client.session["_auth_user_id"]), self.owner.pk)
        response = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("text/html", response["Content-Type"])
        self.assertIn("csrftoken", client.cookies)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), 2)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, self.payload["title"])
        self.assertEqual(created.description, self.payload["description"])
        self.assertEqual(response.data["title"], created.title)

    def test_edit_page_configures_patch_form_with_existing_nullable_values(self):
        from django.templatetags.static import static

        edit_url = reverse("main:update_experience", args=[self.experience.pk])
        for user in (self.editor, self.owner):
            self.client.force_login(user)
            for current in (None, False, True):
                with self.subTest(user=user.username, current=current):
                    self.experience.is_current = current
                    self.experience.end_year = None
                    self.experience.end_month = None
                    self.experience.save()
                    response = self.client.get(edit_url)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
                    self.assertContains(response, 'id="edit-experience-form"')
                    self.assertContains(response, f'data-detail-url="{self.detail_url}"')
                    self.assertContains(response, f'data-experience-id="{self.experience.pk}"')
                    self.assertContains(response, f'action="{edit_url}"')
                    self.assertContains(response, f'src="{static("js/experience.js")}"')
                    self.assertContains(response, 'name="csrfmiddlewaretoken"')
                    form = response.context["form"]
                    self.assertEqual(form["title"].value(), self.payload["title"])
                    self.assertEqual(form["description"].value(), self.payload["description"])
                    self.assertEqual(form["start_year"].value(), 2025)
                    self.assertEqual(form["start_month"].value(), 6)
                    self.assertIsNone(form["end_year"].value())
                    self.assertIsNone(form["end_month"].value())
                    self.assertIs(form["is_current"].value(), current)
                    selected = {None: "unknown", False: "false", True: "true"}[current]
                    self.assertIn(f'value="{selected}" selected', str(form["is_current"]))

    def test_real_session_edit_page_token_allows_patch_and_preserves_stars(self):
        self.editor.set_password(self.owner_password)
        self.editor.save()
        self.experience.starred_by.add(self.visitor, self.editor)
        edit_url = reverse("main:update_experience", args=[self.experience.pk])
        for user in (self.editor, self.owner):
            with self.subTest(user=user.username):
                client = APIClient(enforce_csrf_checks=True)
                self.assertTrue(client.login(username=user.username, password=self.owner_password))
                page = client.get(edit_url)
                self.assertEqual(page.status_code, status.HTTP_200_OK)
                token = client.cookies["csrftoken"].value
                before = self.database_state()
                response = client.patch(
                    self.detail_url, self.payload | {"title": "<b></b>"},
                    format="json", HTTP_X_CSRFTOKEN=token,
                )
                self.assert_validation_error(response, "title")
                self.assertEqual(self.database_state(), before)

                payload = self.payload | {
                    "title": f"Updated by {user.username}",
                    "is_current": None, "end_year": None, "end_month": None,
                }
                response = client.patch(
                    self.detail_url, payload, format="json", HTTP_X_CSRFTOKEN=token,
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.experience.refresh_from_db()
                self.assertEqual(self.experience.title, payload["title"])
                self.assertIsNone(self.experience.is_current)
                self.assertIsNone(self.experience.end_year)
                self.assertIsNone(self.experience.end_month)
                self.assertEqual(self.database_state()[1], before[1])
                record = client.get(self.list_url, {"title": payload["title"]}).data[0]
                self.assertEqual(record["title"], payload["title"])
                self.assertEqual(record["star_count"], 2)

    def test_authenticated_list_uses_two_queries_for_one_four_and_eight_records(self):
        self.experience.starred_by.add(self.visitor)
        self.client.force_authenticate(user=self.visitor)
        for total in (1, 4, 8):
            while Experience.objects.count() < total:
                Experience.objects.create(title="Additional role", description="Description")
            with self.subTest(total=total):
                # Authentication is forced here so session lookups are excluded.
                with self.assertNumQueries(2):
                    response = self.client.get(self.list_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), total)
                record = next(
                    item for item in response.data if item["id"] == str(self.experience.pk)
                )
                self.assertIs(record["is_starred"], True)
                self.assertEqual(record["star_count"], 1)

    def test_serializer_without_request_context_uses_prefetched_stars_safely(self):
        self.experience.starred_by.add(self.visitor)
        experience = Experience.objects.prefetch_related("starred_by").get(
            pk=self.experience.pk
        )

        with self.assertNumQueries(0):
            data = ExperienceSerializer(experience).data

        self.assertEqual(data["id"], str(experience.pk))
        self.assertEqual(data["star_count"], 1)
        self.assertIs(data["is_starred"], False)

    def test_legacy_experience_json_and_ajax_contracts_remain_available(self):
        self.experience.starred_by.add(self.visitor)
        response = self.client.get(reverse("main:get_experiences_json"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        legacy = response.json()[0]
        self.assertEqual(set(legacy), {"model", "pk", "fields"})
        self.assertEqual(legacy["pk"], str(self.experience.pk))
        self.assertEqual(legacy["fields"]["title"], self.payload["title"])
        self.assertNotIn("starred_by", legacy["fields"])

        response = self.client.get(
            reverse("main:get_experiences_ajax"), {"title": "STUDIO"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertIs(payload["is_authenticated"], False)
        self.assertEqual(len(payload["experiences"]), 1)
        record = payload["experiences"][0]
        self.assertEqual(record["pk"], str(self.experience.pk))
        self.assertEqual(record["star_count"], 1)
        self.assertIs(record["is_starred"], False)
        self.assertFalse(record["can_edit"])
        self.assertFalse(record["can_delete"])
        self.assertIsNone(record["star_url"])
