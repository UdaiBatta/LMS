from django.test import TestCase

from course.models import Course, Program
from quiz.models import Choice, MCQuestion, Quiz


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
