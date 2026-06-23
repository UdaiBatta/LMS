from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Student
from course.models import CoursePackage


@receiver(post_save, sender=Student)
def auto_allot_packages(sender, instance, **kwargs):
    """
    When a student is created or updated, auto-enroll them into every active
    course package that targets their program + level + year of study.
    """
    if not (instance.program_id and instance.level and instance.year):
        return

    packages = CoursePackage.objects.filter(
        is_active=True,
        auto_allot=True,
        program_id=instance.program_id,
        level=instance.level,
        year=instance.year,
    )
    for package in packages:
        package.allot(students=[instance])
