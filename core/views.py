from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed

from accounts.decorators import admin_required
from accounts.models import User, Student
from .forms import SessionForm, SemesterForm, NewsAndEventsForm
from .models import NewsAndEvents, ActivityLog, Session, Semester


# ########################################################
# News & Events
# ########################################################
def landing_view(request):
    """Public product overview; authenticated users continue into the app."""
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "core/landing.html")


@login_required
def home_view(request):
    items = NewsAndEvents.objects.all().order_by("-updated_date")
    context = {
        "title": "News & Events",
        "items": items,
    }
    return render(request, "core/index.html", context)


@login_required
@admin_required
def dashboard_view(request):
    # Keep these imports local to avoid coupling the core models to optional
    # feature apps during Django's app-loading phase.
    from course.models import Course, Program, Upload, UploadVideo
    from quiz.models import Quiz, Sitting
    from result.models import TakenCourse

    logs = ActivityLog.objects.all().order_by("-created_at")[:10]
    gender_count = Student.get_gender_count()
    gender_total = gender_count["M"] + gender_count["F"]
    context = {
        "student_count": User.objects.get_student_count(),
        "lecturer_count": User.objects.get_lecturer_count(),
        "superuser_count": User.objects.get_superuser_count(),
        "program_count": Program.objects.count(),
        "course_count": Course.objects.count(),
        "enrollment_count": TakenCourse.objects.count(),
        "quiz_count": Quiz.objects.filter(draft=False).count(),
        "completed_attempt_count": Sitting.objects.filter(complete=True).count(),
        "resource_count": Upload.objects.count() + UploadVideo.objects.count(),
        "current_session": Session.objects.filter(is_current_session=True).first(),
        "current_semester": Semester.objects.filter(is_current_semester=True).first(),
        "males_count": gender_count["M"],
        "females_count": gender_count["F"],
        "males_percentage": round((gender_count["M"] / gender_total) * 100) if gender_total else 0,
        "females_percentage": round((gender_count["F"] / gender_total) * 100) if gender_total else 0,
        "logs": logs,
    }
    return render(request, "core/dashboard.html", context)


@login_required
@admin_required
def post_add(request):
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been uploaded.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm()
    return render(request, "core/post_add.html", {"title": "Add Post", "form": form})


@login_required
@admin_required
def edit_post(request, pk):
    instance = get_object_or_404(NewsAndEvents, pk=pk)
    if request.method == "POST":
        form = NewsAndEventsForm(request.POST, instance=instance)
        title = form.cleaned_data.get("title", "Post") if form.is_valid() else None
        if form.is_valid():
            form.save()
            messages.success(request, f"{title} has been updated.")
            return redirect("home")
        messages.error(request, "Please correct the error(s) below.")
    else:
        form = NewsAndEventsForm(instance=instance)
    return render(request, "core/post_add.html", {"title": "Edit Post", "form": form})


@login_required
@admin_required
def delete_post(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    post = get_object_or_404(NewsAndEvents, pk=pk)
    post_title = post.title
    post.delete()
    messages.success(request, f"{post_title} has been deleted.")
    return redirect("home")


# ########################################################
# Session
# ########################################################
@login_required
@admin_required
def session_list_view(request):
    """Show list of all sessions"""
    sessions = Session.objects.all().order_by("-is_current_session", "-session")
    return render(request, "core/session_list.html", {"sessions": sessions})


@login_required
@admin_required
def session_add_view(request):
    """Add a new session"""
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session()
            form.save()
            messages.success(request, "Session added successfully.")
            return redirect("session_list")
    else:
        form = SessionForm()
    return render(request, "core/session_update.html", {"form": form})


@login_required
@admin_required
def session_update_view(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            if form.cleaned_data.get("is_current_session"):
                unset_current_session(exclude_pk=session.pk)
            form.save()
            messages.success(request, "Session updated successfully.")
            return redirect("session_list")
    else:
        form = SessionForm(instance=session)
    return render(request, "core/session_update.html", {"form": form})


@login_required
@admin_required
def session_delete_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    session = get_object_or_404(Session, pk=pk)
    if session.is_current_session:
        messages.error(request, "You cannot delete the current session.")
    else:
        session.delete()
        messages.success(request, "Session successfully deleted.")
    return redirect("session_list")


def unset_current_session(exclude_pk=None):
    """Unset current session"""
    sessions = Session.objects.filter(is_current_session=True)
    if exclude_pk is not None:
        sessions = sessions.exclude(pk=exclude_pk)
    sessions.update(is_current_session=False)


# ########################################################
# Semester
# ########################################################
@login_required
@admin_required
def semester_list_view(request):
    semesters = Semester.objects.all().order_by("-is_current_semester", "-semester")
    return render(request, "core/semester_list.html", {"semesters": semesters})


@login_required
@admin_required
def semester_add_view(request):
    if request.method == "POST":
        form = SemesterForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester()
            form.save()
            messages.success(request, "Semester added successfully.")
            return redirect("semester_list")
    else:
        form = SemesterForm()
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@admin_required
def semester_update_view(request, pk):
    semester = get_object_or_404(Semester, pk=pk)
    if request.method == "POST":
        form = SemesterForm(request.POST, instance=semester)
        if form.is_valid():
            if form.cleaned_data.get("is_current_semester"):
                unset_current_semester(exclude_pk=semester.pk)
            form.save()
            messages.success(request, "Semester updated successfully!")
            return redirect("semester_list")
    else:
        form = SemesterForm(instance=semester)
    return render(request, "core/semester_update.html", {"form": form})


@login_required
@admin_required
def semester_delete_view(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    semester = get_object_or_404(Semester, pk=pk)
    if semester.is_current_semester:
        messages.error(request, "You cannot delete the current semester.")
    else:
        semester.delete()
        messages.success(request, "Semester successfully deleted.")
    return redirect("semester_list")


def unset_current_semester(exclude_pk=None):
    """Unset current semester"""
    semesters = Semester.objects.filter(is_current_semester=True)
    if exclude_pk is not None:
        semesters = semesters.exclude(pk=exclude_pk)
    semesters.update(is_current_semester=False)
