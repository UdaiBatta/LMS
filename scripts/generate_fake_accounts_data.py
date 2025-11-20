import os
import django
from typing import List

# ------------------- DJANGO ENV SETUP ------------------- #
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from faker import Faker
from factory.django import DjangoModelFactory
from factory import SubFactory, LazyAttribute, Iterator

# Import models
from accounts.models import User, Student, Parent, LEVEL, RELATION_SHIP
from course.models import Program

fake = Faker()


# ------------------- USER FACTORY ------------------- #
class UserFactory(DjangoModelFactory):
    """
    Factory for creating User instances.
    Correctly handles flags for students/parents.
    """

    class Meta:
        model = User

    username = LazyAttribute(lambda _: fake.user_name())
    first_name = LazyAttribute(lambda _: fake.first_name())
    last_name = LazyAttribute(lambda _: fake.last_name())
    email = LazyAttribute(lambda _: fake.email())
    phone = LazyAttribute(lambda _: fake.phone_number())
    address = LazyAttribute(lambda _: fake.address())
    date_joined = timezone.now()

    # Default flags
    is_student = False
    is_parent = False
    is_dep_head = False
    is_lecturer = False

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Extract flags from kwargs (not from class attributes).
        This is the correct factory_boy behaviour.
        """
        is_student = kwargs.pop("is_student", False)
        is_parent = kwargs.pop("is_parent", False)

        user = super()._create(model_class, *args, **kwargs)

        user.is_student = is_student
        user.is_parent = is_parent
        user.save()
        return user


# ------------------- PROGRAM FACTORY ------------------- #
class ProgramFactory(DjangoModelFactory):
    class Meta:
        model = Program

    title = LazyAttribute(lambda _: fake.sentence(nb_words=3))
    summary = LazyAttribute(lambda _: fake.text())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Avoid duplicate program titles.
        """
        program, _ = Program.objects.get_or_create(
            title=kwargs.get("title"), defaults=kwargs
        )
        return program


# ------------------- STUDENT FACTORY ------------------- #
class StudentFactory(DjangoModelFactory):
    class Meta:
        model = Student

    student = SubFactory(UserFactory, is_student=True)
    level = Iterator([choice[0] for choice in LEVEL])
    program = SubFactory(ProgramFactory)


# ------------------- PARENT FACTORY ------------------- #
class ParentFactory(DjangoModelFactory):
    class Meta:
        model = Parent

    user = SubFactory(UserFactory, is_parent=True)
    student = SubFactory(StudentFactory)

    first_name = LazyAttribute(lambda _: fake.first_name())
    last_name = LazyAttribute(lambda _: fake.last_name())
    phone = LazyAttribute(lambda _: fake.phone_number())
    email = LazyAttribute(lambda _: fake.email())

    relation_ship = Iterator([choice[0] for choice in RELATION_SHIP])


# ------------------- MAIN GENERATION FUNCTION ------------------- #
def generate_fake_accounts_data(
    num_programs: int, num_students: int, num_parents: int
) -> None:
    programs: List[Program] = ProgramFactory.create_batch(num_programs)
    students: List[Student] = StudentFactory.create_batch(num_students)
    parents: List[Parent] = ParentFactory.create_batch(num_parents)

    print(f"Created {len(programs)} programs.")
    print(f"Created {len(students)} students.")
    print(f"Created {len(parents)} parents.")


# ------------------- DJANGO-RUNSCRIPT ENTRY POINT ------------------- #
def run():
    """
    Required by django-extensions.
    Running:
        python manage.py runscript generate_fake_data
    will execute this.
    """
    generate_fake_accounts_data(
        num_programs=5,
        num_students=50,
        num_parents=50
    )
    print("Fake LMS data inserted successfully!")
