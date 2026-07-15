from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class ProfileAndPasswordTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="profile-admin",
            email="profile-admin@example.com",
            password="current-password",
            first_name="Profile",
            last_name="Admin",
        )
        self.client.force_login(self.admin)

    def test_admin_profile_uses_the_new_overview_layout(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "profile-overview-layout")
        self.assertContains(response, "Change password")

    def test_admin_can_change_password_and_stays_signed_in(self):
        response = self.client.post(
            reverse("change_password"),
            {
                "old_password": "current-password",
                "new_password1": "new-secure-password-2026",
                "new_password2": "new-secure-password-2026",
            },
        )

        self.assertRedirects(response, reverse("profile"), fetch_redirect_response=False)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("new-secure-password-2026"))
        self.assertEqual(self.client.get(reverse("profile")).status_code, 200)

    def test_password_change_rejects_an_incorrect_current_password(self):
        response = self.client.post(
            reverse("change_password"),
            {
                "old_password": "incorrect-password",
                "new_password1": "new-secure-password-2026",
                "new_password2": "new-secure-password-2026",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your old password was entered incorrectly")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password("current-password"))
