from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.db.models import Avg, Count

from accounts.decorators import lecturer_required
from course.access import lecturer_courses, require_lecturer_course, student_can_access_course
from .forms import (
    EssayForm,
    MCQuestionForm,
    MCQuestionFormSet,
    QuestionForm,
    QuizAddForm,
)
from .models import (
    Course,
    EssayQuestion,
    MCQuestion,
    Progress,
    Question,
    Quiz,
    Sitting,
)


# ########################################################
# Quiz Views
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class QuizCreateView(CreateView):
    model = Quiz
    form_class = QuizAddForm
    template_name = "quiz/quiz_form.html"

    def get_initial(self):
        initial = super().get_initial()
        course = get_object_or_404(Course, slug=self.kwargs["slug"])
        require_lecturer_course(self.request.user, course)
        initial["course"] = course
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = get_object_or_404(Course, slug=self.kwargs["slug"])
        require_lecturer_course(self.request.user, course)
        context["course"] = course
        return context

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs["slug"])
        require_lecturer_course(self.request.user, course)
        form.instance.course = course
        with transaction.atomic():
            self.object = form.save()
            return redirect(
                "mc_create", slug=self.kwargs["slug"], quiz_id=self.object.id
            )


@method_decorator([login_required, lecturer_required], name="dispatch")
class QuizUpdateView(UpdateView):
    model = Quiz
    form_class = QuizAddForm
    template_name = "quiz/quiz_form.html"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Quiz,
            pk=self.kwargs["pk"],
            course__slug=self.kwargs["slug"],
            course__in=lecturer_courses(self.request.user),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.object.course
        return context

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()
            return redirect("quiz_index", self.kwargs["slug"])


@login_required
@lecturer_required
def quiz_delete(request, slug, pk):
    if request.method != "POST":
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(["POST"])
    quiz = get_object_or_404(
        Quiz, pk=pk, course__slug=slug, course__in=lecturer_courses(request.user)
    )
    quiz.delete()
    messages.success(request, "Quiz successfully deleted.")
    return redirect("quiz_index", slug=slug)


@login_required
def quiz_list(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Check if student has access to this course
    has_access = True
    access_message = ""
    
    if request.user.is_student:
        try:
            from accounts.models import Student
            student = Student.objects.get(student=request.user)
            if student.program != course.program:
                has_access = False
                access_message = f"You don't have access to this course. You are enrolled in {student.program.title} program."
        except Student.DoesNotExist:
            has_access = False
            access_message = "Student profile not found. Please contact administration."
    
    if has_access:
        quizzes = Quiz.objects.filter(course=course).order_by("-timestamp")
        
        # For students, add quiz completion status using Sitting model
        quiz_progress = {}
        if request.user.is_student:
            for quiz in quizzes:
                # Check if user has completed this quiz
                completed_sitting = Sitting.objects.filter(
                    user=request.user, 
                    quiz=quiz, 
                    course=course,
                    complete=True
                ).first()
                
                if completed_sitting:
                    quiz_progress[quiz.id] = {
                        'completed': True,
                        'score': completed_sitting.current_score,
                        'total_questions': completed_sitting.get_max_score,
                    }
                else:
                    quiz_progress[quiz.id] = {'completed': False}
    else:
        quizzes = Quiz.objects.none()
        quiz_progress = {}
        messages.error(request, access_message)
    
    context = {
        "quizzes": quizzes,
        "course": course,
        "has_access": has_access,
        "quiz_progress": quiz_progress,
    }
    
    return render(request, "quiz/quiz_list.html", context)


# ########################################################
# Multiple Choice Question Views
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class MCQuestionCreate(CreateView):
    model = MCQuestion
    form_class = MCQuestionForm
    template_name = "quiz/mcquestion_form.html"

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs["quiz"] = get_object_or_404(Quiz, id=self.kwargs["quiz_id"])
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, slug=self.kwargs["slug"])
        require_lecturer_course(self.request.user, context["course"])
        context["quiz_obj"] = get_object_or_404(
            Quiz, id=self.kwargs["quiz_id"], course=context["course"]
        )
        context["quiz_questions_count"] = Question.objects.filter(
            quiz=self.kwargs["quiz_id"]
        ).count()
        if self.request.method == "POST":
            context["formset"] = MCQuestionFormSet(self.request.POST)
        else:
            context["formset"] = MCQuestionFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            with transaction.atomic():
                # Save the MCQuestion instance without committing to the database yet
                self.object = form.save(commit=False)
                self.object.save()

                # Retrieve the Quiz instance
                quiz = get_object_or_404(
                    Quiz, id=self.kwargs["quiz_id"], course=context["course"]
                )

                # set the many-to-many relationship
                self.object.quiz.add(quiz)

                # Save the formset (choices for the question)
                formset.instance = self.object
                formset.save()

                if "another" in self.request.POST:
                    return redirect(
                        "mc_create",
                        slug=self.kwargs["slug"],
                        quiz_id=self.kwargs["quiz_id"],
                    )
                return redirect("quiz_index", slug=self.kwargs["slug"])
        else:
            return self.form_invalid(form)


# ########################################################
# Quiz Progress and Marking Views
# ########################################################


@method_decorator([login_required], name="dispatch")
class QuizUserProgressView(TemplateView):
    template_name = "quiz/progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create progress for current user
        progress, created = Progress.objects.get_or_create(user=user)
        
        # Get category scores (if the method exists and works)
        try:
            context["cat_scores"] = progress.list_all_cat_scores()
        except:
            context["cat_scores"] = {}
        
        # Get completed exams based on user type
        if user.is_superuser:
            exams = Sitting.objects.filter(complete=True).select_related('quiz', 'user', 'course').order_by('-end')
        elif user.is_lecturer:
            # For lecturers, show exams from their courses
            exams = Sitting.objects.filter(
                complete=True,
                quiz__course__allocated_course__lecturer=user
            ).select_related('quiz', 'user', 'course').order_by('-end')
        else:
            # For students, show only their own exams
            exams = Sitting.objects.filter(
                complete=True, 
                user=user
            ).select_related('quiz', 'course').order_by('-end')
        
        context["exams"] = exams
        context["exams_counter"] = exams.count()
        
        # Add some additional context for better UI
        context["user_role"] = user.get_user_role() if hasattr(user, 'get_user_role') else 'Student'
        
        return context


@method_decorator([login_required, lecturer_required], name="dispatch")
class QuizMarkingList(ListView):
    model = Sitting
    template_name = "quiz/quiz_marking_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = Sitting.objects.filter(complete=True)
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                quiz__course__allocated_course__lecturer__pk=self.request.user.id
            )
        quiz_filter = self.request.GET.get("quiz_filter")
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)
        user_filter = self.request.GET.get("user_filter")
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)
        course_filter = self.request.GET.get("course_filter")
        if course_filter:
            queryset = queryset.filter(course__id=course_filter)
        return queryset.select_related('user', 'quiz', 'course').order_by('-end')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(
                allocated_course__lecturer=self.request.user
            ).distinct()
        context['courses'] = courses
        return context


@method_decorator([login_required, lecturer_required], name="dispatch")
class QuizMarkingDetail(DetailView):
    model = Sitting
    template_name = "quiz/quiz_marking_detail.html"

    def get_queryset(self):
        queryset = Sitting.objects.filter(complete=True)
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                quiz__course__in=lecturer_courses(self.request.user)
            )
        return queryset.select_related("quiz", "course", "user")

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()
        question_id = request.POST.get("qid")
        if question_id:
            question = get_object_or_404(
                Question.objects, id=int(question_id), quiz=sitting.quiz
            ).get_subclass()
            if int(question_id) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(question)
            else:
                sitting.add_incorrect_question(question)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["questions"] = self.object.get_questions(with_answers=True)
        return context


# ########################################################
# Quiz Taking View
# ########################################################


@method_decorator([login_required], name="dispatch")
class QuizTake(FormView):
    form_class = QuestionForm
    template_name = "quiz/question.html"
    result_template_name = "quiz/result.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, pk=self.kwargs["pk"])
        self.quiz = get_object_or_404(Quiz, slug=self.kwargs["slug"], course=self.course)
        
        # Check student access to course
        if request.user.is_student:
            try:
                from accounts.models import Student
                student = Student.objects.get(student=request.user)
                if not student_can_access_course(request.user, self.course, require_enrollment=True):
                    messages.error(request, "You must be registered for this course to take its quizzes.")
                    return redirect("user_course_list")
            except Student.DoesNotExist:
                messages.error(request, "Student profile not found. Please contact administration.")
                return redirect("user_course_list")
        elif request.user.is_lecturer:
            require_lecturer_course(request.user, self.course)
        
        # Check if quiz has questions
        if not Question.objects.filter(quiz=self.quiz).exists():
            messages.warning(request, "This quiz has no questions available.")
            return redirect("quiz_index", slug=self.course.slug)

        # Handle quiz sitting
        self.sitting = Sitting.objects.user_sitting(
            request.user, self.quiz, self.course
        )
        if not self.sitting:
            if self.quiz.single_attempt:
                messages.info(
                    request,
                    "You have already completed this quiz. Only one attempt is permitted.",
                )
            else:
                messages.info(
                    request,
                    "You have completed this quiz. You can retake it if allowed.",
                )
            return redirect("quiz_index", slug=self.course.slug)

        # Set self.question and self.progress here
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["question"] = self.question
        return kwargs

    def get_form_class(self):
        if isinstance(self.question, EssayQuestion):
            return EssayForm
        return self.form_class

    def form_valid(self, form):
        self.form_valid_user(form)
        if not self.sitting.get_first_question():
            return self.final_result_user()
        return super().get(self.request)

    def form_valid_user(self, form):
        progress, _ = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data["answers"]
        is_correct = self.question.check_if_correct(guess)

        if is_correct:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if not self.quiz.answers_at_end:
            self.previous = {
                "previous_answer": guess,
                "previous_outcome": is_correct,
                "previous_question": self.question,
                "answers": self.question.get_choices(),
                "question_type": {self.question.__class__.__name__: True},
            }
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

        # Update self.question and self.progress for the next question
        self.question = self.sitting.get_first_question()
        self.progress = self.sitting.progress()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["question"] = self.question
        context["quiz"] = self.quiz
        context["course"] = self.course
        if hasattr(self, "previous"):
            context["previous"] = self.previous
        if hasattr(self, "progress"):
            context["progress"] = self.progress
        return context

    def final_result_user(self):
        self.sitting.mark_quiz_complete()
        results = {
            "course": self.course,
            "quiz": self.quiz,
            "score": self.sitting.get_current_score,
            "max_score": self.sitting.get_max_score,
            "percent": self.sitting.get_percent_correct,
            "sitting": self.sitting,
            "previous": getattr(self, "previous", {}),
        }

        if self.quiz.answers_at_end:
            results["questions"] = self.sitting.get_questions(with_answers=True)
            results["incorrect_questions"] = self.sitting.get_incorrect_questions

        if (
            not self.quiz.exam_paper
            or self.request.user.is_superuser
            or self.request.user.is_lecturer
        ):
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)


# ########################################################
# Quiz Dashboard View
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class QuizDashboardView(TemplateView):
    template_name = "quiz/quiz_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get quizzes based on user role
        if user.is_superuser:
            quizzes = Quiz.objects.all()
            user_courses = Course.objects.all()
        else:
            # For lecturers, get only their courses
            user_courses = Course.objects.filter(
                allocated_course__lecturer=user
            ).distinct()
            quizzes = Quiz.objects.filter(course__in=user_courses)

        # Calculate statistics
        total_quizzes = quizzes.count()
        total_attempts = Sitting.objects.filter(
            quiz__in=quizzes, complete=True
        ).count()

        # Calculate average score
        completed_sittings = Sitting.objects.filter(
            quiz__in=quizzes, complete=True
        )
        if completed_sittings.exists():
            average_score = completed_sittings.aggregate(
                avg=Avg('current_score')
            )['avg'] or 0
        else:
            average_score = 0

        # Recent quizzes (last 10)
        recent_quizzes = quizzes.order_by('-timestamp')[:10]

        # Top performing quizzes
        top_quizzes = []
        for quiz in quizzes[:5]:
            quiz_sittings = completed_sittings.filter(quiz=quiz)
            if quiz_sittings.exists():
                avg_score = quiz_sittings.aggregate(
                    avg=Avg('current_score')
                )['avg'] or 0
                quiz.avg_score = (avg_score / quiz.get_max_score) * 100 if quiz.get_max_score > 0 else 0
                top_quizzes.append(quiz)

        # Sort by average score
        top_quizzes.sort(key=lambda x: x.avg_score, reverse=True)

        # Recent student activity (last 15 attempts)
        recent_attempts = completed_sittings.select_related(
            'user', 'quiz', 'course'
        ).order_by('-end')[:15]

        context.update({
            'total_quizzes': total_quizzes,
            'total_attempts': total_attempts,
            'average_score': round(average_score, 1),
            'active_courses': user_courses.count(),
            'recent_quizzes': recent_quizzes,
            'top_quizzes': top_quizzes[:5],
            'recent_attempts': recent_attempts,
            'user_courses': user_courses,
        })

        return context


# ########################################################
# Quiz Results View
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class QuizResultsView(DetailView):
    model = Quiz
    template_name = "quiz/quiz_results.html"
    context_object_name = "quiz"

    def get_queryset(self):
        return Quiz.objects.filter(course__in=lecturer_courses(self.request.user))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        
        # Get all completed attempts for this quiz
        sittings = Sitting.objects.filter(
            quiz=quiz, complete=True
        ).select_related('user', 'course').order_by('-end')
        
        # Calculate statistics
        total_attempts = sittings.count()
        if total_attempts > 0:
            passed_attempts = sittings.filter(
                current_score__gte=quiz.pass_mark * quiz.get_max_score / 100
            ).count()
            pass_rate = (passed_attempts / total_attempts) * 100
            
            # Score distribution
            scores = [sitting.get_percent_correct for sitting in sittings]
            avg_score = sum(scores) / len(scores) if scores else 0
            min_score = min(scores) if scores else 0
            max_score = max(scores) if scores else 0
            
            # Question analysis
            questions = quiz.get_questions()
            question_stats = []
            for question in questions:
                correct_count = 0
                total_count = 0
                for sitting in sittings:
                    if str(question.id) not in sitting.get_incorrect_questions:
                        correct_count += 1
                    total_count += 1
                
                if total_count > 0:
                    correct_percentage = (correct_count / total_count) * 100
                    question_stats.append({
                        'question': question,
                        'correct_percentage': correct_percentage,
                        'difficulty': 'Easy' if correct_percentage > 80 else 'Medium' if correct_percentage > 60 else 'Hard'
                    })
        else:
            pass_rate = 0
            avg_score = 0
            min_score = 0
            max_score = 0
            question_stats = []
        
        context.update({
            'sittings': sittings,
            'total_attempts': total_attempts,
            'pass_rate': round(pass_rate, 1),
            'avg_score': round(avg_score, 1),
            'min_score': min_score,
            'max_score': max_score,
            'question_stats': question_stats,
        })
        
        return context
