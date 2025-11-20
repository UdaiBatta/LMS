import threading
from datetime import datetime
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.crypto import get_random_string
from core.utils import send_html_email


# -----------------------------
# PASSWORD GENERATION (FIXED)
# -----------------------------
def generate_password(length=10):
    """
    Generate a secure random password.
    This avoids calling make_random_password() on CustomUserManager,
    which caused the AttributeError.
    """
    return get_random_string(length)


# -----------------------------
# STUDENT ID GENERATION
# -----------------------------
def generate_student_id():
    """
    Create a student ID like: STD-2024-15
    Uses prefix from settings.STUDENT_ID_PREFIX
    """
    registered_year = datetime.now().strftime("%Y")
    students_count = get_user_model().objects.filter(is_student=True).count()
    return f"{settings.STUDENT_ID_PREFIX}-{registered_year}-{students_count}"


# -----------------------------
# LECTURER ID GENERATION
# -----------------------------
def generate_lecturer_id():
    """
    Create a lecturer ID like: LEC-2024-3
    Uses prefix from settings.LECTURER_ID_PREFIX
    """
    registered_year = datetime.now().strftime("%Y")
    lecturers_count = get_user_model().objects.filter(is_lecturer=True).count()
    return f"{settings.LECTURER_ID_PREFIX}-{registered_year}-{lecturers_count}"


# -----------------------------
# CREDENTIAL GENERATION
# -----------------------------
def generate_student_credentials():
    """
    Returns (student_id, random_password)
    """
    return generate_student_id(), generate_password()


def generate_lecturer_credentials():
    """
    Returns (lecturer_id, random_password)
    """
    return generate_lecturer_id(), generate_password()


# -----------------------------
# EMAIL THREADING
# -----------------------------
class EmailThread(threading.Thread):
    def __init__(self, subject, recipient_list, template_name, context):
        self.subject = subject
        self.recipient_list = recipient_list
        self.template_name = template_name
        self.context = context
        threading.Thread.__init__(self)

    def run(self):
        send_html_email(
            subject=self.subject,
            recipient_list=self.recipient_list,
            template=self.template_name,
            context=self.context,
        )


# -----------------------------
# SEND NEW ACCOUNT EMAIL
# -----------------------------
def send_new_account_email(user, password):
    """
    Sends either student or lecturer welcome/credentials email.
    """
    if user.is_student:
        template_name = "accounts/email/new_student_account_confirmation.html"
    else:
        template_name = "accounts/email/new_lecturer_account_confirmation.html"

    email = {
        "subject": "Your SkyLearn account confirmation and credentials",
        "recipient_list": [user.email],
        "template_name": template_name,
        "context": {"user": user, "password": password},
    }

    EmailThread(**email).start()
