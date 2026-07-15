from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from course.models import Course, Program
from quiz.models import Choice, MCQuestion, Quiz, Sitting


class MultipleChoiceIntegrityTests(TestCase):
    def setUp(self):
        program = Program.objects.create(title="Science")
        course = Course.objects.create(
            title="Physics",
            code="SCI101",
            program=program,
            level="Bachelor",
            year=1,
            semester="First",
            credit=3,
        )
        quiz = Quiz.objects.create(course=course, title="Physics quiz")
        other_quiz = Quiz.objects.create(course=course, title="Other quiz")
        self.question = MCQuestion.objects.create(content="First question")
        self.question.quiz.add(quiz)
        other_question = MCQuestion.objects.create(content="Other question")
        other_question.quiz.add(other_quiz)
        self.foreign_correct_choice = Choice.objects.create(
            question=other_question,
            choice_text="Correct elsewhere",
            correct=True,
        )

    def test_correct_choice_from_another_question_is_rejected(self):
        guess = str(self.foreign_correct_choice.pk)

        self.assertFalse(self.question.check_if_correct(guess))
        self.assertEqual(self.question.answer_choice_to_string(guess), "")

    @override_settings(
        STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
    )
    def test_marking_a_question_uses_the_concrete_question_type(self):
        marker = get_user_model().objects.create_superuser(
            username="quiz-marker",
            email="marker@example.com",
            password="password",
        )
        sitting = Sitting.objects.create(
            user=marker,
            quiz=self.question.quiz.first(),
            course=self.question.quiz.first().course,
            question_order=f"{self.question.pk},",
            question_list="",
            incorrect_questions="",
            current_score=1,
            complete=True,
        )
        self.client.force_login(marker)

        with translation.override("en"):
            response = self.client.post(
                reverse("quiz_marking_detail", kwargs={"pk": sitting.pk}),
                {"qid": self.question.pk},
                secure=True,
            )

        self.assertEqual(response.status_code, 200)
        sitting.refresh_from_db()
        self.assertIn(self.question.pk, sitting.get_incorrect_questions)
