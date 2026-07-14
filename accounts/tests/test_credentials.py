from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class CredentialIsolationTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_one = user_model.objects.create_superuser(
            username="admin-one",
            email="admin-one@example.com",
            password="password",
        )
        self.admin_two = user_model.objects.create_superuser(
            username="admin-two",
            email="admin-two@example.com",
            password="password",
        )
        self.student_user = user_model.objects.create_user(
            username="new-student",
            email="new-student@example.com",
            password="password",
        )
        cache.set(
            f"student_credentials:{self.student_user.pk}",
            {
                "username": "generated-id",
                "password": "generated-password",
                "student_name": "New Student",
            },
            timeout=300,
        )

    def test_new_credentials_are_visible_only_to_creating_admin_session(self):
        creating_client = Client()
        creating_client.force_login(self.admin_one)
        session = creating_client.session
        session["new_student_credentials_id"] = self.student_user.pk
        session.save()

        other_client = Client()
        other_client.force_login(self.admin_two)
        other_response = other_client.get(reverse("student_credentials"))
        self.assertRedirects(
            other_response,
            reverse("student_list"),
            fetch_redirect_response=False,
        )

        response = creating_client.get(reverse("student_credentials"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "generated-id")
        self.assertContains(response, "generated-password")

    def test_student_delete_requires_post(self):
        client = Client()
        client.force_login(self.admin_one)

        response = client.get(
            reverse("student_delete", kwargs={"pk": self.student_user.pk})
        )

        self.assertEqual(response.status_code, 405)
