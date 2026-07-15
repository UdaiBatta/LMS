from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import Semester, Session
from course.models import Course, Program
from quiz.models import Quiz


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class LandingPageTests(TestCase):
    @override_settings(SKYLEARN_CONTACT_EMAIL="sales@example.com")
    def test_anonymous_visitor_sees_public_landing_page_and_login_action(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")
        self.assertContains(response, reverse("login"))
        self.assertContains(response, "img/brand.svg")
        self.assertContains(response, "A clearer way to run learning")
        self.assertContains(response, "public-showcase")
        self.assertContains(response, 'data-pulse-step="0"')
        self.assertContains(response, "public-pulse-status")
        self.assertContains(response, "data-role-filter=\"student\"")
        self.assertContains(response, "js/landing.js")
        self.assertContains(response, "Contact us for pricing")
        self.assertContains(response, "mailto:sales@example.com")

    def test_authenticated_visitor_continues_to_application_home(self):
        user = get_user_model().objects.create_user(
            username="landing-user",
            email="landing-user@example.com",
            password="password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("landing"))

        self.assertRedirects(response, reverse("home"), fetch_redirect_response=False)


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class AcademicPeriodWorkflowTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="period-admin",
            email="period-admin@example.com",
            password="password",
        )
        self.client.force_login(self.admin)

    def test_adding_current_semester_keeps_current_session(self):
        session = Session.objects.create(
            session="2026/2027",
            is_current_session=True,
            next_session_begins="2027-07-01",
        )

        response = self.client.post(
            reverse("add_semester"),
            {
                "semester": "First",
                "is_current_semester": "True",
                "session": session.pk,
                "next_semester_begins": "2027-01-01",
            },
        )

        self.assertRedirects(
            response, reverse("semester_list"), fetch_redirect_response=False
        )
        session.refresh_from_db()
        self.assertTrue(session.is_current_session)
        self.assertTrue(Semester.objects.get().is_current_semester)

    def test_common_create_pages_use_guided_progressive_forms(self):
        for url_name in ("add_item", "add_student", "add_lecturer", "add_program"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "record-form-layout")
                self.assertContains(response, "data-form-progress")
                self.assertContains(response, "record-form-actions")

    def test_setting_current_session_unsets_all_previous_sessions(self):
        old_one = Session.objects.create(session="2024/2025", is_current_session=True)
        old_two = Session.objects.create(session="2025/2026", is_current_session=True)

        self.client.post(
            reverse("add_session"),
            {
                "session": "2026/2027",
                "is_current_session": "True",
                "next_session_begins": "2027-07-01",
            },
        )

        old_one.refresh_from_db()
        old_two.refresh_from_db()
        self.assertFalse(old_one.is_current_session)
        self.assertFalse(old_two.is_current_session)
        self.assertEqual(Session.objects.filter(is_current_session=True).count(), 1)

    def test_seventh_semester_can_be_configured_as_current(self):
        session = Session.objects.create(session="2026")

        response = self.client.post(
            reverse("add_semester"),
            {
                "semester": "Seventh",
                "is_current_semester": "True",
                "session": session.pk,
                "next_semester_begins": "2027-01-01",
            },
        )

        self.assertRedirects(
            response, reverse("semester_list"), fetch_redirect_response=False
        )
        semester = Semester.objects.get(semester="Seventh", session=session)
        self.assertTrue(semester.is_current_semester)

    def test_delete_semester_requires_post(self):
        session = Session.objects.create(session="2026/2027")
        semester = Semester.objects.create(semester="First", session=session)

        response = self.client.get(
            reverse("delete_semester", kwargs={"pk": semester.pk})
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Semester.objects.filter(pk=semester.pk).exists())

    def test_dashboard_uses_live_academic_metrics(self):
        program = Program.objects.create(title="Dashboard Program")
        course = Course.objects.create(
            title="Dashboard Course",
            code="DASH101",
            program=program,
            level="Bachelor",
            year=1,
            semester="First",
            credit=3,
        )
        Quiz.objects.create(course=course, title="Published Quiz", draft=False)
        Quiz.objects.create(course=course, title="Draft Quiz", draft=True)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["program_count"], 1)
        self.assertEqual(response.context["course_count"], 1)
        self.assertEqual(response.context["quiz_count"], 1)
        self.assertContains(response, "Published quizzes")
        self.assertNotContains(response, "Lab Assistance")


# Create your tests here.
