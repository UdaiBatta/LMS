from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import CreateView
from django_filters.views import FilterView
from django.utils.translation import gettext as _

from accounts.decorators import admin_required, lecturer_required, student_required
from accounts.models import Student
from core.models import Semester, Session
from course.filters import CourseAllocationFilter, ProgramFilter
from course.forms import (
    CourseAddForm,
    CourseAllocationForm,
    CoursePackageForm,
    EditCourseAllocationForm,
    ProgramForm,
    UploadFormFile,
    UploadFormVideo,
)
from course.models import (
    Course,
    CourseAllocation,
    CoursePackage,
    Program,
    Upload,
    UploadVideo,
)
from result.models import TakenCourse
from course.access import require_lecturer_course, student_can_access_course


# ########################################################
# Program Views
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class ProgramFilterView(FilterView):
    filterset_class = ProgramFilter
    template_name = "course/program_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Programs"
        return context


@login_required
@admin_required
def program_add(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, f"{program.title} program has been created.")
            return redirect("programs")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = ProgramForm()
    return render(
        request, "course/program_add.html", {"title": "Add Program", "form": form}
    )


@login_required
def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)
    courses = Course.objects.filter(program_id=pk).order_by("-year")
    credits = courses.aggregate(total_credits=Sum("credit"))
    paginator = Paginator(courses, 10)
    page = request.GET.get("page")
    courses = paginator.get_page(page)
    return render(
        request,
        "course/program_single.html",
        {
            "title": program.title,
            "program": program,
            "courses": courses,
            "credits": credits,
        },
    )


@login_required
@admin_required
def program_edit(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            messages.success(request, f"{program.title} program has been updated.")
            return redirect("programs")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = ProgramForm(instance=program)
    return render(
        request, "course/program_add.html", {"title": "Edit Program", "form": form}
    )


@login_required
@admin_required
def program_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    program = get_object_or_404(Program, pk=pk)
    title = program.title
    program.delete()
    messages.success(request, f"Program {title} has been deleted.")
    return redirect("programs")


# ########################################################
# Course Views
# ########################################################


@login_required
def course_single(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.user.is_student and not student_can_access_course(
        request.user, course, require_enrollment=True
    ):
        messages.error(request, "You are not enrolled in this course.")
        return redirect("user_course_list")
    if request.user.is_lecturer:
        require_lecturer_course(request.user, course)
    elif not (request.user.is_student or request.user.is_superuser):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("You do not have access to this course.")
    files = Upload.objects.filter(course__slug=slug)
    videos = UploadVideo.objects.filter(course__slug=slug)
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)
    
    # Get quizzes for this course
    from quiz.models import Quiz
    quizzes = Quiz.objects.filter(course=course)
    if request.user.is_student:
        quizzes = quizzes.filter(draft=False)
    quizzes = quizzes.order_by('-timestamp')
    
    return render(
        request,
        "course/course_single.html",
        {
            "title": course.title,
            "course": course,
            "files": files,
            "videos": videos,
            "lecturers": lecturers,
            "quizzes": quizzes,
            "media_url": settings.MEDIA_URL,
            "has_access": True,
            "student_registered": True,
        },
    )


@login_required
@admin_required
def course_add(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        form = CourseAddForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(
                request, f"{course.title} ({course.code}) has been created."
            )
            return redirect("program_detail", pk=program.pk)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(initial={"program": program})
    return render(
        request,
        "course/course_add.html",
        {"title": "Add Course", "form": form, "program": program},
    )


@login_required
@admin_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == "POST":
        form = CourseAddForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(
                request, f"{course.title} ({course.code}) has been updated."
            )
            return redirect("program_detail", pk=course.program.pk)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(instance=course)
    return render(
        request, "course/course_add.html", {"title": "Edit Course", "form": form}
    )


@login_required
@admin_required
def course_delete(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    course = get_object_or_404(Course, slug=slug)
    title = course.title
    program_id = course.program.id
    course.delete()
    messages.success(request, f"Course {title} has been deleted.")
    return redirect("program_detail", pk=program_id)


# ########################################################
# Course Allocation Views
# ########################################################


@method_decorator([login_required, admin_required], name="dispatch")
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = "course/course_allocation_form.html"

    def form_valid(self, form):
        lecturer = form.cleaned_data["lecturer"]
        selected_courses = form.cleaned_data["courses"]
        allocation, created = CourseAllocation.objects.get_or_create(lecturer=lecturer)
        allocation.courses.set(selected_courses)
        messages.success(
            self.request, f"Courses allocated to {lecturer.get_full_name()} successfully."
        )
        return redirect("course_allocation_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Assign Course"
        return context


@method_decorator([login_required, admin_required], name="dispatch")
class CourseAllocationFilterView(FilterView):
    filterset_class = CourseAllocationFilter
    template_name = "course/course_allocation_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Course Allocations"
        return context


@login_required
@admin_required
def edit_allocated_course(request, pk):
    allocation = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == "POST":
        form = EditCourseAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            messages.success(request, "Course allocation has been updated.")
            return redirect("course_allocation_view")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = EditCourseAllocationForm(instance=allocation)
    return render(
        request,
        "course/course_allocation_form.html",
        {"title": "Edit Course Allocation", "form": form},
    )


@login_required
@admin_required
def deallocate_course(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    allocation = get_object_or_404(CourseAllocation, pk=pk)
    allocation.delete()
    messages.success(request, "Successfully deallocated courses.")
    return redirect("course_allocation_view")


# ########################################################
# Student Enrollment Views (allocate courses to students)
# ########################################################


@login_required
@admin_required
def course_enrollment_list(request):
    """Overview of every course with its enrolled-student count."""
    courses = (
        Course.objects.select_related("program")
        .annotate(enrolled_count=Count("taken_courses"))
        .order_by("program__title", "level", "year", "semester", "title")
    )
    return render(
        request,
        "course/course_enrollment_list.html",
        {"title": _("Student Enrollment"), "courses": courses},
    )


@login_required
@admin_required
def enroll_students(request):
    """
    Registrar-style enrollment for a single course.

    Shows the class roster (enrolled students, with a Drop action) and an
    "Add students" panel that searches the whole student body with filters
    (program / level / name / ID). Students with recorded scores are protected
    from accidental removal.
    """
    courses = Course.objects.select_related("program").order_by(
        "program__title", "level", "year", "semester", "title"
    )

    course_id = request.POST.get("course") or request.GET.get("course")
    selected_course = (
        get_object_or_404(Course, pk=course_id) if course_id else None
    )

    # Filters for the "add students" panel
    q = request.GET.get("q", "").strip()
    filter_program = request.GET.get("program", "")
    filter_level = request.GET.get("level", "")

    if request.method == "POST" and selected_course:
        action = request.POST.get("action")

        if action == "add":
            ids = [i for i in request.POST.getlist("students") if i.isdigit()]
            added = 0
            for student in Student.objects.filter(pk__in=ids):
                _obj, created = TakenCourse.objects.get_or_create(
                    student=student, course=selected_course
                )
                added += 1 if created else 0
            if added:
                messages.success(
                    request,
                    _("Added %(n)d student(s) to %(course)s.")
                    % {"n": added, "course": selected_course.title},
                )
            else:
                messages.info(request, _("No new students were added."))

        elif action == "remove":
            tc = (
                TakenCourse.objects.filter(
                    course=selected_course, student_id=request.POST.get("student")
                )
                .select_related("student__student")
                .first()
            )
            if tc and tc.total and tc.total > 0:
                messages.warning(
                    request,
                    _(
                        "%(name)s has recorded scores and was not removed. "
                        "Clear their scores first if you really want to drop them."
                    )
                    % {"name": tc.student.student.get_full_name()},
                )
            elif tc:
                tc.delete()
                messages.info(request, _("Student dropped from the course."))

        # Preserve the course + active filters across the redirect
        params = {"course": selected_course.pk}
        for key in ("q", "program", "level"):
            val = request.POST.get(key, "")
            if val:
                params[key] = val
        return redirect(f"{reverse('enroll_students')}?{urlencode(params)}")

    roster = []
    candidates = []
    total_candidates = 0
    if selected_course:
        roster = (
            TakenCourse.objects.filter(course=selected_course)
            .select_related("student__student", "student__program")
            .order_by("student__student__first_name", "student__student__last_name")
        )
        enrolled_ids = roster.values_list("student_id", flat=True)

        cand_qs = (
            Student.objects.select_related("student", "program")
            .exclude(pk__in=list(enrolled_ids))
        )
        # Default to the course's own program for convenience; "all" shows everyone
        if filter_program == "":
            filter_program = str(selected_course.program_id)
        if filter_program and filter_program != "all":
            cand_qs = cand_qs.filter(program_id=filter_program)
        if filter_level:
            cand_qs = cand_qs.filter(level=filter_level)
        if q:
            cand_qs = cand_qs.filter(
                Q(student__first_name__icontains=q)
                | Q(student__last_name__icontains=q)
                | Q(student__username__icontains=q)
            )
        cand_qs = cand_qs.order_by("student__first_name", "student__last_name")
        total_candidates = cand_qs.count()
        candidates = cand_qs[:200]  # cap for performance; refine with filters

    return render(
        request,
        "course/enroll_students.html",
        {
            "title": _("Enroll Students"),
            "courses": courses,
            "selected_course": selected_course,
            "roster": roster,
            "candidates": candidates,
            "total_candidates": total_candidates,
            "candidate_cap": 200,
            "programs": Program.objects.order_by("title"),
            "level_choices": settings.LEVEL_CHOICES,
            "q": q,
            "filter_program": filter_program,
            "filter_level": filter_level,
        },
    )


# ########################################################
# Course Package Views (pre-selected subjects auto-allotted to a cohort)
# ########################################################


@login_required
@admin_required
def package_list(request):
    packages = (
        CoursePackage.objects.select_related("program")
        .prefetch_related("courses")
        .all()
    )
    rows = []
    for pkg in packages:
        rows.append({"package": pkg, "student_count": pkg.matching_students().count()})
    return render(
        request,
        "course/package_list.html",
        {"title": _("Course Packages"), "rows": rows},
    )


@login_required
@admin_required
def package_add(request):
    if request.method == "POST":
        form = CoursePackageForm(request.POST)
        if form.is_valid():
            package = form.save()
            messages.success(
                request,
                _("Package '%(name)s' created. Click 'Allot now' to enroll current students.")
                % {"name": package.name},
            )
            return redirect("package_list")
        messages.error(request, _("Correct the error(s) below."))
    else:
        form = CoursePackageForm()
    return render(
        request,
        "course/package_form.html",
        {"title": _("Create Course Package"), "form": form},
    )


@login_required
@admin_required
def package_edit(request, pk):
    package = get_object_or_404(CoursePackage, pk=pk)
    if request.method == "POST":
        form = CoursePackageForm(request.POST, instance=package)
        if form.is_valid():
            form.save()
            messages.success(request, _("Package updated."))
            return redirect("package_list")
        messages.error(request, _("Correct the error(s) below."))
    else:
        form = CoursePackageForm(instance=package)
    return render(
        request,
        "course/package_form.html",
        {"title": _("Edit Course Package"), "form": form, "package": package},
    )


@login_required
@admin_required
def package_allot(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    package = get_object_or_404(CoursePackage, pk=pk)
    created, student_count = package.allot()
    messages.success(
        request,
        _(
            "Allotted '%(name)s': %(created)d new enrollment(s) across "
            "%(students)d student(s)."
        )
        % {"name": package.name, "created": created, "students": student_count},
    )
    return redirect("package_list")


@login_required
@admin_required
def package_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    package = get_object_or_404(CoursePackage, pk=pk)
    name = package.name
    package.delete()
    messages.success(request, _("Deleted package '%(name)s'.") % {"name": name})
    return redirect("package_list")


# ########################################################
# File Upload Views
# ########################################################


@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)
    require_lecturer_course(request.user, course)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.course = course
            upload.save()
            messages.success(request, f"{upload.title} has been uploaded.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormFile()
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "File Upload", "form": form, "course": course},
    )


@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = get_object_or_404(Course, slug=slug)
    require_lecturer_course(request.user, course)
    upload = get_object_or_404(Upload, pk=file_id, course=course)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES, instance=upload)
        if form.is_valid():
            upload = form.save()
            messages.success(request, f"{upload.title} has been updated.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormFile(instance=upload)
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "Edit File", "form": form, "course": course},
    )


@login_required
@lecturer_required
def handle_file_delete(request, slug, file_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    course = get_object_or_404(Course, slug=slug)
    require_lecturer_course(request.user, course)
    upload = get_object_or_404(Upload, pk=file_id, course=course)
    title = upload.title
    upload.delete()
    messages.success(request, f"{title} has been deleted.")
    return redirect("course_detail", slug=slug)


# ########################################################
# Video Upload Views
# ########################################################


@login_required
@lecturer_required
def handle_video_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)
    require_lecturer_course(request.user, course)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.course = course
            video.save()
            messages.success(request, f"{video.title} has been uploaded.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormVideo()
    return render(
        request,
        "upload/upload_video_form.html",
        {"title": "Video Upload", "form": form, "course": course},
    )


@login_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    if request.user.is_student and not student_can_access_course(request.user, course):
        messages.error(request, "You are not enrolled in this course.")
        return redirect("user_course_list")
    if request.user.is_lecturer:
        require_lecturer_course(request.user, course)
    elif not (request.user.is_student or request.user.is_superuser):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("You do not have access to this course.")
    video = get_object_or_404(UploadVideo, slug=video_slug, course=course)
    return render(
        request,
        "upload/video_single.html",
        {"video": video, "course": course},
    )


@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    require_lecturer_course(request.user, course)
    video = get_object_or_404(UploadVideo, slug=video_slug, course=course)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video = form.save()
            messages.success(request, f"{video.title} has been updated.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormVideo(instance=video)
    return render(
        request,
        "upload/upload_video_form.html",
        {"title": "Edit Video", "form": form, "course": course},
    )


@login_required
@lecturer_required
def handle_video_delete(request, slug, video_slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    course = get_object_or_404(Course, slug=slug)
    require_lecturer_course(request.user, course)
    video = get_object_or_404(UploadVideo, slug=video_slug, course=course)
    title = video.title
    video.delete()
    messages.success(request, f"{title} has been deleted.")
    return redirect("course_detail", slug=slug)


# ########################################################
# Course Registration Views
# ########################################################


@login_required
@student_required
def course_registration(request):
    """
    Handle course registration for students with proper timing controls.
    Students can only register:
    1. Before semester starts (registration period)
    2. Not during active semester
    """
    try:
        student = get_object_or_404(Student, student__id=request.user.id)
    except Student.DoesNotExist:
        messages.error(request, _("Student profile not found. Please contact administrator."))
        return redirect('user_course_list')
    
    if not student.program:
        messages.error(request, _("You are not assigned to a program. Please contact administrator."))
        return redirect('user_course_list')
    
    # Get current semester and session
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    current_session = Session.objects.filter(is_current_session=True).first()
    
    if not current_semester or not current_session:
        messages.error(request, _("No active semester or session found. Course registration is not available."))
        return render(request, "course/course_registration.html", {
            "no_semester": True,
            "student": student,
            "error_message": "No active semester or session configured."
        })

    # Check if registration is allowed (you can customize this logic based on your needs)
    registration_allowed = True
    registration_message = ""
    
    # Example: Check if we're in registration period vs active semester
    # You might want to add date-based checks here
    from datetime import date
    today = date.today()
    
    # If semester has begun (you can customize this logic)
    if current_semester.next_semester_begins and today >= current_semester.next_semester_begins:
        registration_allowed = False
        registration_message = _("Course registration is closed. The semester has already begun.")
    
    # You could also add specific registration period dates to the Semester model
    # For now, we'll allow registration but with a warning during active semester
    
    if request.method == "POST":
        if not registration_allowed:
            messages.error(request, registration_message)
            return redirect("course_registration")
            
        ids = []
        data = request.POST.copy()
        data.pop("csrfmiddlewaretoken", None)  # remove csrf_token
        
        for key in data.keys():
            if key.isdigit():  # Ensure we only process course IDs
                ids.append(int(key))
        
        if not ids:
            messages.warning(request, _("No courses selected for registration."))
            return redirect("course_registration")
        
        # Check for duplicate registrations and validate courses
        already_registered = []
        newly_registered = []
        invalid_courses = []
        
        for course_id in ids:
            try:
                course = Course.objects.get(
                    pk=course_id,
                    program=student.program,
                    level=student.level,
                )
                existing = TakenCourse.objects.filter(student=student, course=course).exists()
                
                if not existing:
                    TakenCourse.objects.create(student=student, course=course)
                    newly_registered.append(course.title)
                else:
                    already_registered.append(course.title)
            except Course.DoesNotExist:
                invalid_courses.append(f"Course ID {course_id}")
        
        # Provide feedback
        if newly_registered:
            messages.success(request, _("Successfully registered for: %s") % ", ".join(newly_registered))
        
        if already_registered:
            messages.warning(request, _("Already registered for: %s") % ", ".join(already_registered))
            
        if invalid_courses:
            messages.error(request, _("Invalid courses: %s") % ", ".join(invalid_courses))
        
        return redirect("course_registration")
    
    else:
        # GET request - show registration form
        
        # Get taken courses
        taken_courses = TakenCourse.objects.filter(student=student)
        taken_course_ids = [tc.course.pk for tc in taken_courses]

        # Available courses for registration (excluding already taken)
        available_courses = Course.objects.filter(
            program=student.program,
            level=student.level,
        ).exclude(id__in=taken_course_ids).order_by("year", "title")
        
        # All courses in program for statistics
        all_program_courses = Course.objects.filter(
            level=student.level, 
            program=student.program
        )

        # Calculate statistics
        registered_courses = Course.objects.filter(id__in=taken_course_ids, level=student.level)
        
        no_course_is_registered = registered_courses.count() == 0
        all_courses_are_registered = registered_courses.count() == all_program_courses.count()

        # Calculate credits
        total_first_semester_credit = sum(
            course.credit for course in available_courses if course.semester == "First"
        )
        total_second_semester_credit = sum(
            course.credit for course in available_courses if course.semester == "Second"  
        )
        total_registered_credit = sum(course.credit for course in registered_courses)
        
        context = {
            "is_calender_on": True,
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "current_semester": current_semester,
            "current_session": current_session,
            "courses": available_courses,
            "total_first_semester_credit": total_first_semester_credit,
            "total_sec_semester_credit": total_second_semester_credit,
            "registered_courses": registered_courses,
            "total_registered_credit": total_registered_credit,
            "student": student,
            "registration_allowed": registration_allowed,
            "registration_message": registration_message,
        }
        return render(request, "course/course_registration.html", context)


@login_required
@student_required
def course_drop(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    student = get_object_or_404(Student, student__pk=request.user.id)
    current_semester = Semester.objects.filter(is_current_semester=True).first()
    from django.utils import timezone

    if (
        current_semester
        and current_semester.next_semester_begins
        and timezone.localdate() >= current_semester.next_semester_begins
    ):
        messages.error(
            request,
            _("Courses cannot be dropped after the registration period closes."),
        )
        return redirect("course_registration")

    course_ids = [
        course_id
        for course_id in request.POST.getlist("course_ids")
        if course_id.isdigit()
    ]
    registrations = TakenCourse.objects.filter(
        student=student, course_id__in=course_ids
    )
    protected = registrations.filter(total__gt=0).count()
    dropped = registrations.filter(total=0).delete()[0]

    if dropped:
        messages.success(
            request, _("%(count)d course registration(s) dropped.") % {"count": dropped}
        )
    if protected:
        messages.warning(
            request,
            _(
                "%(count)d course(s) with recorded scores were not dropped. "
                "Contact an administrator if a correction is required."
            )
            % {"count": protected},
        )
    if not dropped and not protected:
        messages.info(request, _("No matching course registrations were found."))
    return redirect("course_registration")


# ########################################################
# User Course List View (UPDATED)
# ########################################################


@login_required
def user_course_list(request):
    """Display courses based on user type with enhanced functionality for students"""
    
    if request.user.is_lecturer:
        # Lecturers see courses they teach
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id).distinct()
        template = 'course/user_course_list.html'
        context_title = _('My Teaching Courses')
        
        # Add pagination for lecturers
        paginator = Paginator(courses, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'courses': page_obj,
            'title': context_title,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
        }
        
    elif request.user.is_student:
        # Students see courses from their enrolled program
        try:
            student = Student.objects.get(student=request.user)
            if student.program:
                # Get all courses from student's program
                program_courses = Course.objects.filter(
                    program=student.program
                ).annotate(
                    file_count=Count('upload', distinct=True),
                    video_count=Count('uploadvideo', distinct=True),
                    quiz_count=Count(
                        'quiz', filter=Q(quiz__draft=False), distinct=True
                    ),
                ).distinct().order_by('year', 'semester', 'title')
                
                # Get courses the student has registered for
                taken_courses = TakenCourse.objects.filter(student=student)
                taken_course_ids = [tc.course.id for tc in taken_courses]
                
                # Add pagination
                paginator = Paginator(program_courses, 12)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)
                
                context = {
                    'courses': page_obj,
                    'student': student,
                    'taken_courses': taken_courses,
                    'taken_course_ids': taken_course_ids,
                    'course_count': paginator.count,
                    'registered_count': len(taken_course_ids),
                    'program': student.program,
                    'title': _('My Courses'),
                    'is_paginated': page_obj.has_other_pages(),
                    'page_obj': page_obj,
                }
            else:
                context = {
                    'courses': [],
                    'student': student,
                    'title': _('My Courses'),
                    'no_program': True,
                }
                messages.warning(request, _("Please contact admin to assign you to a program."))
                
        except Student.DoesNotExist:
            context = {
                'courses': [],
                'title': _('My Courses'),
                'no_student_profile': True,
            }
            messages.error(request, _("Student profile not found. Please contact admin."))
            
        template = 'course/student_course_list.html'
        
    elif request.user.is_superuser:
        # Admins see all courses
        courses = Course.objects.all().order_by('program', 'year', 'semester')
        template = 'course/user_course_list.html'
        context_title = _('All Courses')
        
        # Add pagination for admins
        paginator = Paginator(courses, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'courses': page_obj,
            'title': context_title,
            'is_paginated': page_obj.has_other_pages(),
            'page_obj': page_obj,
        }
        
    else:
        # Other users see no courses
        context = {
            'courses': [],
            'title': _('Available Courses'),
            'no_access': True,
        }
        template = 'course/user_course_list.html'

    return render(request, template, context)


