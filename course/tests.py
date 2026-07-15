from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Student
from core.models import Semester, Session
from course.forms import CoursePackageForm
from course.models import Course, CourseAllocation, Program
from quiz.models import Quiz
from result.models import TakenCourse


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
        self.foreign_quiz = Quiz.objects.create(
            course=self.other_course, title="Foreign"
        )

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

    def test_student_course_list_distinguishes_registered_course_access(self):
        student_user = get_user_model().objects.create_user(
            username="course-list-student",
            email="course-list-student@example.com",
            password="password",
        )
        student_user.is_student = True
        student_user.save()
        student = Student.objects.create(
            student=student_user, program=self.program, level="Bachelor", year=1
        )
        TakenCourse.objects.create(student=student, course=self.course)
        Quiz.objects.create(course=self.course, title="Published", draft=False)
        Quiz.objects.create(course=self.course, title="Hidden Draft", draft=True)
        self.client.force_login(student_user)

        response = self.client.get(reverse("user_course_list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["course_count"], 2)
        self.assertEqual(response.context["registered_count"], 1)
        courses = {course.pk: course for course in response.context["courses"]}
        self.assertEqual(courses[self.course.pk].quiz_count, 1)
        self.assertContains(response, "Open course")
        self.assertContains(response, "Register to access")

    def test_student_quiz_list_renders_without_artificial_loader(self):
        student_user = get_user_model().objects.create_user(
            username="quiz-list-student",
            email="quiz-list-student@example.com",
            password="password",
        )
        student_user.is_student = True
        student_user.save()
        student = Student.objects.create(
            student=student_user, program=self.program, level="Bachelor", year=1
        )
        TakenCourse.objects.create(student=student, course=self.course)
        Quiz.objects.create(course=self.course, title="Visible Quiz", draft=False)
        self.client.force_login(student_user)

        response = self.client.get(
            reverse("quiz_index", kwargs={"slug": self.course.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visible Quiz")
        self.assertNotContains(response, "progress-card")

    def test_lecturer_cannot_open_an_unallocated_course(self):
        self.client.force_login(self.lecturer)

        response = self.client.get(
            reverse("course_detail", kwargs={"slug": self.other_course.slug})
        )

        self.assertEqual(response.status_code, 403)

    def test_course_detail_uses_real_lecturer_information_without_placeholder_links(self):
        self.client.force_login(self.lecturer)

        response = self.client.get(
            reverse("course_detail", kwargs={"slug": self.course.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Course lecturer")
        self.assertNotContains(response, "Donec sed odio dui")
        self.assertNotContains(response, "fab fa-twitter")

    def test_quiz_update_cannot_move_quiz_to_another_course(self):
        quiz = Quiz.objects.create(course=self.course, title="Owned")
        self.client.force_login(self.lecturer)

        response = self.client.post(
            reverse(
                "quiz_update",
                kwargs={"slug": self.course.slug, "pk": quiz.pk},
            ),
            {
                "title": "Updated",
                "course": self.other_course.pk,
                "description": "",
                "category": "practice",
                "pass_mark": 50,
            },
        )

        self.assertRedirects(
            response,
            reverse("quiz_index", kwargs={"slug": self.course.slug}),
            fetch_redirect_response=False,
        )
        quiz.refresh_from_db()
        self.assertEqual(quiz.course, self.course)

    def test_student_cannot_take_a_draft_quiz(self):
        user_model = get_user_model()
        student_user = user_model.objects.create_user(
            username="draft-student",
            email="draft-student@example.com",
            password="password",
        )
        student_user.is_student = True
        student_user.save()
        student = Student.objects.create(
            student=student_user, program=self.program, level="Bachelor"
        )
        TakenCourse.objects.create(student=student, course=self.course)
        quiz = Quiz.objects.create(course=self.course, title="Draft", draft=True)
        self.client.force_login(student_user)

        response = self.client.get(
            reverse("quiz_take", kwargs={"pk": quiz.pk, "slug": quiz.slug})
        )

        self.assertEqual(response.status_code, 403)

    def test_student_cannot_register_for_a_different_level_by_forging_post(self):
        session = Session.objects.create(session="2026/2027", is_current_session=True)
        Semester.objects.create(
            semester="First",
            session=session,
            is_current_semester=True,
        )
        postgraduate_course = Course.objects.create(
            title="Advanced Algorithms",
            code="ENG501",
            program=self.program,
            level="Master",
            year=1,
            semester="First",
            credit=3,
        )
        user_model = get_user_model()
        student_user = user_model.objects.create_user(
            username="registration-student",
            email="registration-student@example.com",
            password="password",
        )
        student_user.is_student = True
        student_user.save()
        student = Student.objects.create(
            student=student_user, program=self.program, level="Bachelor"
        )
        self.client.force_login(student_user)

        response = self.client.post(
            reverse("course_registration"),
            {str(postgraduate_course.pk): "on"},
        )

        self.assertRedirects(
            response,
            reverse("course_registration"),
            fetch_redirect_response=False,
        )
        self.assertFalse(
            TakenCourse.objects.filter(
                student=student, course=postgraduate_course
            ).exists()
        )

    def test_student_cannot_drop_a_course_with_recorded_scores(self):
        user_model = get_user_model()
        student_user = user_model.objects.create_user(
            username="drop-student",
            email="drop-student@example.com",
            password="password",
        )
        student_user.is_student = True
        student_user.save()
        student = Student.objects.create(
            student=student_user, program=self.program, level="Bachelor"
        )
        enrollment = TakenCourse.objects.create(
            student=student,
            course=self.course,
            assignment=10,
        )
        self.client.force_login(student_user)

        response = self.client.post(
            reverse("course_drop"), {"course_ids": [self.course.pk]}
        )

        self.assertRedirects(
            response,
            reverse("course_registration"),
            fetch_redirect_response=False,
        )
        self.assertTrue(TakenCourse.objects.filter(pk=enrollment.pk).exists())

    def test_course_package_rejects_courses_from_another_cohort(self):
        form = CoursePackageForm(
            {
                "name": "First year package",
                "program": self.program.pk,
                "level": "Bachelor",
                "year": 1,
                "courses": [self.other_course.pk],
                "auto_allot": "on",
                "is_active": "on",
            }
        )
        self.other_course.year = 2
        self.other_course.save()

        # Rebind after changing the fixture so validation sees the mismatch.
        form = CoursePackageForm(form.data)
        self.assertFalse(form.is_valid())
        self.assertIn("courses", form.errors)
