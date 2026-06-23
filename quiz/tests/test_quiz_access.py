from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Student
from course.models import Program, Course
from quiz.models import Quiz, Sitting


class QuizViewTestCase(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.user.is_student = True
        self.user.save()
        
        # Create test program
        self.program = Program.objects.create(
            title='Computer Science',
            summary='Test program'
        )
        
        # Create student profile
        self.student = Student.objects.create(
            student=self.user,
            id_number='12345',
            program=self.program,
            level='100'
        )
        
        # Create test course
        self.course = Course.objects.create(
            title='Programming 101',
            code='CS101',
            program=self.program,
            year=1,
            semester='First',
            credit=3,
            level='100'
        )
        
        # Create test quiz
        self.quiz = Quiz.objects.create(
            course=self.course,
            title='Test Quiz',
            description='A test quiz'
        )
        
        self.client = Client()
    
    def test_quiz_list_access(self):
        """Test that students can access quiz list for their program courses"""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('quiz_index', args=[self.course.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quiz.title)
    
    def test_quiz_progress_tracking(self):
        """Test that quiz progress is tracked correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a completed sitting
        sitting = Sitting.objects.create(
            user=self.user,
            quiz=self.quiz,
            course=self.course,
            question_order='',
            question_list='',
            current_score=8,
            complete=True
        )
        
        url = reverse('quiz_index', args=[self.course.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('quiz_progress', response.context)
