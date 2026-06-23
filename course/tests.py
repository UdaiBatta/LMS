from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Student
from course.models import Course, CourseAllocation, Program
from quiz.models import Quiz


@override_settings(
    SECURE_SSL_REDIRECT=False,
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
)
class CourseAuthorizationTests(TestCase):
    def setUp(self):
        self.program = Program.objects.create(title="Engineering")
        self.course = Course.objects.create(
            title="Algorithms",
            code="ENG101",
            program=self.program,
            level="Bachelor",
            year=1,
            semester="First",
            credit=3,
        )
        self.other_course = Course.objects.create(
            title="Networks",
            code="ENG102",
            program=self.program,
            level="Bachelor",
            year=1,
            semester="First",
            credit=3,
        )
        user_model = get_user_model()
        self.lecturer = user_model.objects.create_user(
            username="lecturer", email="lecturer@example.com", password="password"
        )
        self.lecturer.is_lecturer = True
        self.lecturer.save()
        allocation = CourseAllocation.objects.create(lecturer=self.lecturer)
        allocation.courses.add(self.course)
        self.foreign_quiz = Quiz.objects.create(course=self.other_course, title="Foreign")

    def test_lecturer_cannot_update_a_quiz_for_an_unallocated_course(self):
        self.client.force_login(self.lecturer)

        response = self.client.get(
            reverse(
                "quiz_update",
                kwargs={"slug": self.other_course.slug, "pk": self.foreign_quiz.pk},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_quiz_delete_requires_post(self):
        quiz = Quiz.objects.create(course=self.course, title="Owned")
        self.client.force_login(self.lecturer)

        response = self.client.get(
            reverse("quiz_delete", kwargs={"slug": self.course.slug, "pk": quiz.pk})
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Quiz.objects.filter(pk=quiz.pk).exists())

    def test_student_cannot_open_an_unregistered_course(self):
        user_model = get_user_model()
        student_user = user_model.objects.create_user(
            username="student", email="student@example.com", password="password"
        )
        student_user.is_student = True
        student_user.save()
        Student.objects.create(
            student=student_user, program=self.program, level="Bachelor"
        )
        self.client.force_login(student_user)

        response = self.client.get(
            reverse("course_detail", kwargs={"slug": self.course.slug})
        )

        self.assertRedirects(
            response, reverse("user_course_list"), fetch_redirect_response=False
        )
