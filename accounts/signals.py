from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth import get_user_model

from .utils import (
    generate_student_credentials,
    generate_lecturer_credentials,
    send_new_account_email,
)

User = get_user_model()


@receiver(post_save, sender=User)
def post_save_account_receiver(sender, instance, created, **kwargs):
    """
    Automatically generate username/password and send email
    for new students & lecturers.
    """

    # Only run this once on creation
    if not created:
        return

    # --- STUDENT ACCOUNT HANDLING ---
    if instance.is_student:
        username, password = generate_student_credentials()

        # Assign credentials safely without causing infinite loop
        # Use update() to avoid triggering the signal again
        User.objects.filter(pk=instance.pk).update(
            username=username
        )
        instance.set_password(password)
        instance.save(update_fields=["password"])

        # Refresh instance to get updated username before sending email
        instance.refresh_from_db()
        
        # Email
        email_sent = send_new_account_email(instance, password)

        # Cache last created student info
        cache.set(
            f"student_credentials:{instance.pk}",
            {
                "username": username,
                "password": password,
                "student_name": instance.get_full_name(),
                "student_email": instance.email,
                "email_status": "sent" if email_sent else "failed",
            },
            timeout=300,
        )

    # --- LECTURER ACCOUNT HANDLING ---
    if instance.is_lecturer:
        username, password = generate_lecturer_credentials()

        # Avoid recursion → use update()
        User.objects.filter(pk=instance.pk).update(
            username=username
        )
        instance.set_password(password)
        instance.save(update_fields=["password"])

        # Refresh instance to get updated username before sending email
        instance.refresh_from_db()
        
        # Email
        send_new_account_email(instance, password)
