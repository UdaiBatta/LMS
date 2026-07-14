from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Student
from core.models import Semester, Session
from course.models import Course, CourseAllocation, Program
from result.models import Result, TakenCourse


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class ScoreEntryAuthorizationTests(TestCase):
    def setUp(self):
        self.session = Session.objects.create(
            session="2026/2027", is_current_session=True
        )
        self.semester = Semester.objects.create(
            semester="First",
            session=self.session,
            is_current_semester=True,
        )
        program = Program.objects.create(title="Engineering")
        self.course = Course.objects.create(
            title="Algorithms",
            code="ENG201",
            program=program,
            level="Bachelor",
            year=1,
            semester="First",
            credit=3,
        )
        self.foreign_course = Course.objects.create(
            title="Networks",
            code="ENG202",
            program=program,
            level="Bachelor",
            year=1,
            semester="First",
            credit=3,
        )
        user_model = get_user_model()
        self.lecturer = user_model.objects.create_user(
            username="lecturer",
            email="lecturer-score@example.com",
            password="password",
            is_lecturer=True,
        )
        allocation = CourseAllocation.objects.create(lecturer=self.lecturer)
        allocation.courses.add(self.course)

        student_user = user_model.objects.create_user(
            username="student-score",
            email="student-score@example.com",
            password="password",
        )
        student_user.is_student = True
        student_user.save()
        student = Student.objects.create(
            student=student_user, program=program, level="Bachelor"
        )
        self.enrollment = TakenCourse.objects.create(
            student=student, course=self.course
        )
        self.foreign_enrollment = TakenCourse.objects.create(
            student=student, course=self.foreign_course
        )
        self.client.force_login(self.lecturer)

    def score_payload(self, enrollment, values=None):
        return {str(enrollment.pk): values or ["10", "20", "10", "10", "50"]}

    def test_lecturer_cannot_open_an_unallocated_course_score_sheet(self):
        response = self.client.get(
            reverse("add_score_for", kwargs={"id": self.foreign_course.pk})
        )

        self.assertEqual(response.status_code, 404)

    def test_forged_enrollment_id_cannot_change_another_course(self):
        response = self.client.post(
            reverse("add_score_for", kwargs={"id": self.course.pk}),
            self.score_payload(self.foreign_enrollment),
        )

        self.assertEqual(response.status_code, 400)
        self.foreign_enrollment.refresh_from_db()
        self.assertEqual(self.foreign_enrollment.total, Decimal("0.00"))

    def test_valid_scores_are_saved_and_result_is_updated(self):
        response = self.client.post(
            reverse("add_score_for", kwargs={"id": self.course.pk}),
            self.score_payload(self.enrollment),
        )

        self.assertRedirects(
            response,
            reverse("add_score_for", kwargs={"id": self.course.pk}),
            fetch_redirect_response=False,
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.total, Decimal("100.00"))
        self.assertEqual(
            Result.objects.filter(
                student=self.enrollment.student,
                semester=self.semester.semester,
                session=self.session.session,
            ).count(),
            1,
        )

    def test_score_components_cannot_total_more_than_100(self):
        response = self.client.post(
            reverse("add_score_for", kwargs={"id": self.course.pk}),
            self.score_payload(self.enrollment, ["30", "30", "30", "30", "30"]),
        )

        self.assertEqual(response.status_code, 400)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.total, Decimal("0.00"))


# Create your tests here.
