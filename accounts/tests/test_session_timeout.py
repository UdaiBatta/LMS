import json
import time

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    SESSION_COOKIE_AGE=60,
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class SessionTimeoutTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="session-user",
            email="session-user@example.com",
            password="password",
        )
        self.client.force_login(self.user)
        self.url = reverse("session_timeout_check")

    def set_last_activity(self, value):
        session = self.client.session
        session["last_activity"] = value
        session.save()

    def test_status_poll_does_not_refresh_activity(self):
        original_activity = time.time() - 10
        self.set_last_activity(original_activity)

        response = self.client.post(
            self.url, data="{}", content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["authenticated"])
        self.assertAlmostEqual(
            self.client.session["last_activity"], original_activity, places=3
        )

    def test_expired_poll_logs_out_and_returns_json(self):
        self.set_last_activity(time.time() - 61)

        response = self.client.post(
            self.url, data="{}", content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["authenticated"])
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_explicit_extension_refreshes_activity(self):
        original_activity = time.time() - 10
        self.set_last_activity(original_activity)

        response = self.client.post(
            self.url,
            data=json.dumps({"extend": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertGreater(self.client.session["last_activity"], original_activity)

    def test_login_page_never_renders_or_enforces_session_monitoring(self):
        self.set_last_activity(time.time() - 61)

        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertNotContains(response, "sessionTimeoutModal")
        self.assertNotContains(response, "session-status-float")

    def test_authenticated_app_uses_the_compact_session_countdown(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "session-countdown")
        self.assertContains(response, "float-progress")
        self.assertNotContains(response, "border-warning shadow-lg")
