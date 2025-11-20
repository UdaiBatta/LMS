import os
import django
import random
from random import choice
from typing import Type, List

# ---------- DJANGO ENV SETUP (must be before model imports) ----------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from faker import Faker
from factory.django import DjangoModelFactory
from factory import SubFactory, LazyAttribute, Iterator, LazyFunction, post_generation

from course.models import (
    Program,
    Course,
    CourseAllocation,
    Upload,
    UploadVideo,
    CourseOffer,
)
from accounts.models import User, DepartmentHead
from core.models import Session

# reuse factories from other scripts
from .generate_fake_accounts_data import UserFactory, ProgramFactory
from .generate_fake_core_data import SessionFactory

fake = Faker()


# ---------- Department Head ---------- #
class DepartmentHeadFactory(DjangoModelFactory):
    class Meta:
        model = DepartmentHead

    user = SubFactory(UserFactory, is_dep_head=True)
    department = SubFactory(ProgramFactory)  # Program = department


# ---------- Courses ---------- #
class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    slug = LazyAttribute(lambda _: fake.slug())
    title = LazyAttribute(lambda _: fake.sentence(nb_words=4))
    code = LazyAttribute(lambda _: fake.unique.bothify(text="CSE###"))
    credit = LazyAttribute(lambda _: fake.random_int(min=1, max=6))
    summary = LazyAttribute(lambda _: fake.paragraph())
    program: Type[Program] = SubFactory(ProgramFactory)
    level = Iterator(["Beginner", "Intermediate", "Advanced"])
    year = LazyAttribute(lambda _: fake.random_int(min=1, max=4))
    semester = Iterator([c[0] for c in settings.SEMESTER_CHOICES])
    is_elective = LazyAttribute(lambda _: fake.boolean())


# ---------- Course Allocation (lecturer + session + courses) ---------- #
class CourseAllocationFactory(DjangoModelFactory):
    class Meta:
        model = CourseAllocation

    lecturer: Type[User] = SubFactory(UserFactory, is_lecturer=True)
    session: Type[Session] = SubFactory(SessionFactory)

    @post_generation
    def courses(self, create, extracted, **kwargs):
        """
        Attach 1–N random courses to this allocation.
        If `courses=` is passed explicitly, use that instead.
        """
        if not create:
            return

        if extracted:
            self.courses.set(extracted)
            return

        all_courses = list(Course.objects.all())
        if not all_courses:
            return

        num = random.randint(1, min(5, len(all_courses)))
        self.courses.set(random.sample(all_courses, num))


# ---------- Uploads (files) ---------- #
class UploadFactory(DjangoModelFactory):
    class Meta:
        model = Upload

    title = LazyAttribute(lambda _: fake.sentence(nb_words=3))
    course = SubFactory(CourseFactory)
    # just store a fake path; file doesn't have to exist for testing
    file = LazyAttribute(lambda _: f"uploads/{fake.file_name(extension='pdf')}")
    updated_date = LazyFunction(fake.date_time_this_year)
    upload_time = LazyFunction(fake.date_time_this_year)


# ---------- Upload Videos ---------- #
class UploadVideoFactory(DjangoModelFactory):
    class Meta:
        model = UploadVideo

    title = LazyAttribute(lambda _: fake.sentence(nb_words=3))
    slug = LazyAttribute(lambda _: fake.slug())
    course = SubFactory(CourseFactory)
    video = LazyAttribute(lambda _: f"videos/{fake.file_name(extension='mp4')}")
    summary = LazyAttribute(lambda _: fake.paragraph())
    timestamp = LazyFunction(fake.date_time_this_year)


# ---------- Course Offers ---------- #
class CourseOfferFactory(DjangoModelFactory):
    class Meta:
        model = CourseOffer

    dep_head = SubFactory(DepartmentHeadFactory)


# ---------- MAIN GENERATOR FUNCTION ---------- #
def generate_fake_course_data(
    num_programs: int,
    num_courses: int,
    num_course_allocations: int,
    num_uploads: int,
    num_upload_videos: int,
    num_course_offers: int,
) -> None:
    """
    Generate fake data for course-related models.
    """
    programs: List[Program] = ProgramFactory.create_batch(num_programs)
    print(f"Created {len(programs)} programs.")

    courses: List[Course] = CourseFactory.create_batch(num_courses)
    print(f"Created {len(courses)} courses.")

    course_allocations: List[CourseAllocation] = CourseAllocationFactory.create_batch(
        num_course_allocations
    )
    print(f"Created {len(course_allocations)} course allocations.")

    uploads: List[Upload] = UploadFactory.create_batch(num_uploads)
    print(f"Created {len(uploads)} uploads.")

    upload_videos: List[UploadVideo] = UploadVideoFactory.create_batch(num_upload_videos)
    print(f"Created {len(upload_videos)} upload videos.")

    course_offers: List[CourseOffer] = CourseOfferFactory.create_batch(num_course_offers)
    print(f"Created {len(course_offers)} course offers.")


# ---------- ENTRY POINT FOR `runscript` ---------- #
def run():
    generate_fake_course_data(
        num_programs=5,
        num_courses=20,
        num_course_allocations=10,
        num_uploads=20,
        num_upload_videos=10,
        num_course_offers=5,
    )
    print("✅ Fake course data generated successfully.")
