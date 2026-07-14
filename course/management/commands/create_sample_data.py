from django.core.management.base import BaseCommand
from course.models import Program, Course
from quiz.models import Quiz, MCQuestion, Choice
from accounts.models import User


class Command(BaseCommand):
    help = 'Create sample quiz data for ALL courses in the COE program'

    def add_arguments(self, parser):
        parser.add_argument(
            '--program',
            type=str,
            default='Computer and Electronic Engineering',
            help='Program name to create quizzes for (default: Computer and Electronic Engineering)',
        )

    def handle(self, *args, **options):
        program_name = options['program']
        
        # Get or create the specified program
        try:
            program = Program.objects.get(title__icontains=program_name)
            self.stdout.write(f'Found program: {program.title}')
        except Program.DoesNotExist:
            # Create the program if it doesn't exist
            program, created = Program.objects.get_or_create(
                title=program_name,
                defaults={
                    "summary": f"A comprehensive program covering various engineering and technology subjects."
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created program: {program.title}')
                )

        # Get all courses in this program
        courses = Course.objects.filter(program=program)
        
        if not courses.exists():
            self.stdout.write(
                self.style.WARNING(f'No courses found for program: {program.title}')
            )
            self.stdout.write('Creating some sample courses...')
            
            # Create sample courses if none exist
            sample_courses = [
                {
                    "code": "COE301",
                    "title": "Database Management Systems",
                    "credit": 3,
                    "summary": "Introduction to database concepts, SQL, normalization, and database design principles.",
                    "level": "Bachelor",
                    "year": 3,
                    "semester": "First"
                },
                {
                    "code": "COE302",
                    "title": "Data Structures and Algorithms",
                    "credit": 4,
                    "summary": "Fundamental data structures and algorithmic techniques for problem solving.",
                    "level": "Bachelor",
                    "year": 3,
                    "semester": "First"
                },
                {
                    "code": "COE303",
                    "title": "Computer Networks",
                    "credit": 3,
                    "summary": "Introduction to computer networking protocols and network architecture.",
                    "level": "Bachelor",
                    "year": 3,
                    "semester": "Second"
                },
                {
                    "code": "COE304",
                    "title": "Software Engineering",
                    "credit": 3,
                    "summary": "Software development methodologies, design patterns, and project management.",
                    "level": "Bachelor",
                    "year": 3,
                    "semester": "Second"
                },
                {
                    "code": "COE305",
                    "title": "Web Development",
                    "credit": 3,
                    "summary": "Modern web development technologies including HTML, CSS, JavaScript, and frameworks.",
                    "level": "Bachelor",
                    "year": 3,
                    "semester": "First"
                }
            ]
            
            for course_data in sample_courses:
                course, created = Course.objects.get_or_create(
                    code=course_data["code"],
                    defaults={
                        **course_data,
                        "program": program,
                        "is_elective": False
                    }
                )
                if created:
                    self.stdout.write(f'Created course: {course.title} ({course.code})')
            
            # Refresh courses list
            courses = Course.objects.filter(program=program)

        self.stdout.write(f'\nCreating quizzes for {courses.count()} courses in {program.title}...\n')

        # Quiz templates for different course types
        quiz_templates = {
            "database": {
                "questions": [
                    {
                        "content": "What does SQL stand for?",
                        "choices": [
                            ("Structured Query Language", True),
                            ("Simple Query Language", False),
                            ("Standard Query Language", False),
                            ("System Query Language", False)
                        ],
                        "explanation": "SQL stands for Structured Query Language, used to communicate with databases."
                    },
                    {
                        "content": "Which is a primary key constraint?",
                        "choices": [
                            ("Allows NULL values", False),
                            ("Allows duplicate values", False),
                            ("Uniquely identifies each record", True),
                            ("Must be a number", False)
                        ],
                        "explanation": "A primary key uniquely identifies each record and cannot contain NULL values."
                    }
                ]
            },
            "programming": {
                "questions": [
                    {
                        "content": "What is the time complexity of binary search?",
                        "choices": [
                            ("O(n)", False),
                            ("O(log n)", True),
                            ("O(n²)", False),
                            ("O(1)", False)
                        ],
                        "explanation": "Binary search has O(log n) time complexity as it halves the search space each iteration."
                    },
                    {
                        "content": "Which data structure uses LIFO principle?",
                        "choices": [
                            ("Queue", False),
                            ("Stack", True),
                            ("Array", False),
                            ("Tree", False)
                        ],
                        "explanation": "Stack follows Last In First Out (LIFO) principle."
                    }
                ]
            },
            "networking": {
                "questions": [
                    {
                        "content": "What layer does HTTP operate at in the OSI model?",
                        "choices": [
                            ("Physical Layer", False),
                            ("Network Layer", False),
                            ("Transport Layer", False),
                            ("Application Layer", True)
                        ],
                        "explanation": "HTTP operates at the Application Layer (Layer 7) of the OSI model."
                    },
                    {
                        "content": "What is the default port for HTTPS?",
                        "choices": [
                            ("80", False),
                            ("443", True),
                            ("8080", False),
                            ("22", False)
                        ],
                        "explanation": "HTTPS uses port 443 by default for secure web communication."
                    }
                ]
            },
            "general": {
                "questions": [
                    {
                        "content": "What does API stand for?",
                        "choices": [
                            ("Application Programming Interface", True),
                            ("Advanced Programming Interface", False),
                            ("Automated Programming Interface", False),
                            ("Application Process Interface", False)
                        ],
                        "explanation": "API stands for Application Programming Interface."
                    },
                    {
                        "content": "Which is an example of agile methodology?",
                        "choices": [
                            ("Waterfall", False),
                            ("Spiral", False),
                            ("Scrum", True),
                            ("V-Model", False)
                        ],
                        "explanation": "Scrum is a popular agile software development framework."
                    }
                ]
            }
        }

        # Create quizzes for each course
        for course in courses:
            # Determine quiz type based on course title keywords
            course_title_lower = course.title.lower()
            if any(keyword in course_title_lower for keyword in ['database', 'sql', 'dbms']):
                quiz_type = "database"
            elif any(keyword in course_title_lower for keyword in ['algorithm', 'programming', 'data structure']):
                quiz_type = "programming"
            elif any(keyword in course_title_lower for keyword in ['network', 'internet', 'protocol']):
                quiz_type = "networking"
            else:
                quiz_type = "general"

            # Create quiz for this course
            quiz, created = Quiz.objects.get_or_create(
                title=f"{course.title} - Fundamentals Quiz",
                course=course,
                defaults={
                    "description": f"Test your knowledge of {course.title} concepts and principles.",
                    "category": "practice",
                    "pass_mark": 70,
                    "random_order": True,
                    "answers_at_end": True,
                    "exam_paper": True,
                    "single_attempt": False,
                    "draft": False
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created quiz: {quiz.title}')
                )

                # Add questions based on the quiz type
                questions_data = quiz_templates[quiz_type]["questions"]
                
                for q_data in questions_data:
                    question = MCQuestion.objects.create(
                        content=q_data["content"],
                        explanation=q_data["explanation"],
                        choice_order="content"
                    )
                    question.quiz.add(quiz)

                    # Create choices
                    for choice_text, is_correct in q_data["choices"]:
                        Choice.objects.create(
                            question=question,
                            choice_text=choice_text,
                            correct=is_correct
                        )

                    self.stdout.write(f'  + Added question: {question.content[:40]}...')
                    
                # Create an additional mid-term and final exam quiz
                for quiz_category, quiz_suffix in [("assignment", "Assignment"), ("exam", "Final Exam")]:
                    extra_quiz, extra_created = Quiz.objects.get_or_create(
                        title=f"{course.title} - {quiz_suffix}",
                        course=course,
                        defaults={
                            "description": f"{quiz_suffix} for {course.title}",
                            "category": quiz_category,
                            "pass_mark": 80 if quiz_category == "exam" else 60,
                            "random_order": True,
                            "answers_at_end": False if quiz_category == "exam" else True,
                            "exam_paper": True,
                            "single_attempt": True if quiz_category == "exam" else False,
                            "draft": False
                        }
                    )
                    
                    if extra_created:
                        self.stdout.write(f'  ✓ Created {quiz_suffix.lower()}: {extra_quiz.title}')
                        
                        # Add a sample question to the extra quiz
                        sample_question = MCQuestion.objects.create(
                            content=f"This is a sample {quiz_suffix.lower()} question for {course.title}.",
                            explanation=f"Sample explanation for {course.title} {quiz_suffix.lower()}.",
                            choice_order="content"
                        )
                        sample_question.quiz.add(extra_quiz)
                        
                        # Add sample choices
                        choices = [
                            ("Option A - Correct Answer", True),
                            ("Option B - Incorrect", False),
                            ("Option C - Incorrect", False),
                            ("Option D - Incorrect", False)
                        ]
                        
                        for choice_text, is_correct in choices:
                            Choice.objects.create(
                                question=sample_question,
                                choice_text=choice_text,
                                correct=is_correct
                            )

            else:
                self.stdout.write(f'• Quiz already exists: {quiz.title}')

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('QUIZ CREATION SUMMARY:')
        self.stdout.write('='*60)
        
        for course in courses:
            quizzes = Quiz.objects.filter(course=course)
            self.stdout.write(f'\n📚 {course.title} ({course.code}):')
            for quiz in quizzes:
                question_count = quiz.get_questions().count()
                self.stdout.write(f'  • {quiz.title} - {question_count} questions [{quiz.category}]')
                
        total_quizzes = Quiz.objects.filter(course__program=program).count()
        self.stdout.write(f'\n🎯 Total quizzes created for {program.title}: {total_quizzes}')
        self.stdout.write('\n' + self.style.SUCCESS('✅ Quiz creation completed for all courses!'))
        
        if courses.exists():
            sample_course = courses.first()
            self.stdout.write(f'\n🔗 Access quizzes at: /quiz/{sample_course.slug}/quizzes/')
            self.stdout.write(f'🔗 Quiz Dashboard: /quiz/dashboard/')
