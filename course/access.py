"""Centralized, server-side authorization rules for course-owned data."""

from django.core.exceptions import PermissionDenied


def lecturer_courses(user):
    """Return only courses a lecturer may manage; superusers may manage all."""
    from course.models import Course

    if user.is_superuser:
        return Course.objects.all()
    return Course.objects.filter(allocated_course__lecturer=user).distinct()


def require_lecturer_course(user, course):
    if not lecturer_courses(user).filter(pk=course.pk).exists():
        raise PermissionDenied("You are not allocated to this course.")
    return course


def student_can_access_course(user, course, *, require_enrollment=True):
    """Return whether a student belongs to a course and, when requested, enrolled."""
    if user.is_superuser or user.is_lecturer:
        return True
    if not user.is_student:
        return False

    from accounts.models import Student
    from result.models import TakenCourse

    try:
        student = Student.objects.get(student=user)
    except Student.DoesNotExist:
        return False
    if student.program_id != course.program_id:
        return False
    return not require_enrollment or TakenCourse.objects.filter(
        student=student, course=course
    ).exists()
