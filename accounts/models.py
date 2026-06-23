from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager, BaseUserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.validators import EmailValidator, RegexValidator
from PIL import Image

from course.models import Program


# -----------------------------
# VALIDATORS
# -----------------------------

# Email validator with custom error message
email_validator = EmailValidator(
    message=_("Enter a valid email address.")
)

# Phone number validator - supports international formats
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=_("Phone number must be 9-15 digits. Country code is optional. Format: '+999999999' or '999999999'")
)

# Alternative phone validator for more flexible formats
phone_validator_flexible = RegexValidator(
    regex=r'^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$',
    message=_("Enter a valid phone number. Examples: +1234567890, (123) 456-7890, 123-456-7890")
)


# -----------------------------
# CONSTANTS
# -----------------------------

GENDERS = (
    ("M", _("Male")),
    ("F", _("Female")),
)

BACHELOR_DEGREE = "Bachelor"
MASTER_DEGREE = "Master"

LEVEL = (
    (BACHELOR_DEGREE, _("Bachelor Degree")),
    (MASTER_DEGREE, _("Master Degree")),
)

RELATION_SHIP = (
    ("Father", _("Father")),
    ("Mother", _("Mother")),
    ("Brother", _("Brother")),
    ("Sister", _("Sister")),
    ("Grand Mother", _("Grand Mother")),
    ("Grand Father", _("Grand Father")),
    ("Other", _("Other")),
)


# -----------------------------
# CUSTOM USER MANAGER
# -----------------------------

class CustomUserManager(UserManager):
    """
    Extends Django's UserManager with additional search/count utilities.
    ALL Django default functionality (create_user, create_superuser, etc.)
    is preserved because we inherit from UserManager.
    """

    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            qs = qs.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            ).distinct()
        return qs

    def get_student_count(self):
        return self.model.objects.filter(is_student=True).count()

    def get_lecturer_count(self):
        return self.model.objects.filter(is_lecturer=True).count()

    def get_superuser_count(self):
        return self.model.objects.filter(is_superuser=True).count()


# -----------------------------
# MAIN USER MODEL
# -----------------------------

class User(AbstractUser):
    """
    The core authentication user with extended fields
    for SkyLearn LMS.
    """

    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)

    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    
    # Enhanced phone field with validation
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[phone_validator_flexible],
        help_text=_("Enter phone number in format: +1234567890 or (123) 456-7890")
    )
    
    address = models.CharField(max_length=255, blank=True, null=True)

    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/",
        default="default.png",
        null=True,
        blank=True,
    )

    # Override email to add validation (Django's built-in email field already has EmailValidator)
    email = models.EmailField(
        _('email address'),
        unique=True,  # Make email unique
        help_text=_("Enter a valid email address"),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"

    def get_user_role(self):
        if self.is_superuser:
            return _("Admin")
        if self.is_student:
            return _("Student")
        if self.is_lecturer:
            return _("Lecturer")
        if self.is_parent:
            return _("Parent")
        if self.is_dep_head:
            return _("Department Head")
        return _("User")

    def get_picture(self):
        if self.picture:
            try:
                return self.picture.url
            except:
                return settings.MEDIA_URL + "default.png"
        return settings.MEDIA_URL + "default.png"

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"user_id": self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize image safely
        try:
            if self.picture and self.picture.path:
                img = Image.open(self.picture.path)
                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300))
                    img.save(self.picture.path)
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        if self.picture and self.picture.name != "default.png":
            try:
                self.picture.delete(save=False)
            except:
                pass
        super().delete(*args, **kwargs)


# -----------------------------
# STUDENT MODEL
# -----------------------------

class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query:
            qs = qs.filter(
                Q(level__icontains=query) |
                Q(program__title__icontains=query)
            ).distinct()
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    year = models.IntegerField(
        choices=settings.YEARS,
        default=1,
        null=True,
        blank=True,
        help_text="Current year of study",
    )
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    objects = StudentManager()

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self):
        return self.student.get_full_name()

    @classmethod
    def get_gender_count(cls):
        return {
            "M": cls.objects.filter(student__gender="M").count(),
            "F": cls.objects.filter(student__gender="F").count(),
        }

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"user_id": self.student.id})

    def delete(self, *args, **kwargs):
        self.student.delete()
        super().delete(*args, **kwargs)


# -----------------------------
# PARENT MODEL
# -----------------------------

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    relation_ship = models.CharField(max_length=20, choices=RELATION_SHIP)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return self.user.username


# -----------------------------
# DEPARTMENT HEAD MODEL
# -----------------------------

class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return f"{self.user.username}"
