from django import forms
from django.conf import settings
from django.db import transaction
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
)
from django.contrib.auth.forms import PasswordResetForm
from course.models import Program
from .models import User, Student, Parent, RELATION_SHIP, LEVEL, GENDERS


class StaffAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Username",
        required=False,
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "placeholder": "+1234567890 or (123) 456-7890",
                "pattern": r"^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
            }
        ),
        label="Mobile No.",
        help_text="Enter phone number in format: +1234567890 or (123) 456-7890",
        required=False,
    )

    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "type": "email",
                "class": "form-control",
                "placeholder": "user@example.com",
            }
        ),
        label="Email",
        help_text="Enter a valid email address",
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
        required=False,
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
        required=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            "username",
            "first_name", 
            "last_name",
            "gender",
            "address",
            "phone",
            "email",
            "password1",
            "password2",
        ]

    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces, dashes, and parentheses for validation
            import re
            clean_phone = re.sub(r'[-.\s\(\)]', '', phone)
            # Check if it contains only digits and optional plus sign
            if not re.match(r'^\+?\d{9,15}$', clean_phone):
                raise forms.ValidationError(
                    "Enter a valid phone number with 9-15 digits. "
                    "Format: +1234567890 or (123) 456-7890"
                )
        return phone

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()

        return user


class StudentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"type": "text", "class": "form-control", "id": "username_id"}
        ),
        label="Username",
        required=False,
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "placeholder": "+1234567890 or (123) 456-7890",
                "pattern": r"^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
            }
        ),
        label="Mobile No.",
        help_text="Enter phone number in format: +1234567890 or (123) 456-7890",
        required=False,
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    level = forms.CharField(
        widget=forms.Select(
            choices=LEVEL,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Program",
    )

    year = forms.TypedChoiceField(
        choices=settings.YEARS,
        coerce=int,
        initial=1,
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Year of study",
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
        required=False,
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
        required=False,
    )

    # def validate_email(self):
    #     email = self.cleaned_data['email']
    #     if User.objects.filter(email__iexact=email, is_active=True).exists():
    #         raise forms.ValidationError("Email has taken, try another email address. ")

    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces, dashes, and parentheses for validation
            import re
            clean_phone = re.sub(r'[-.\s\(\)]', '', phone)
            # Check if it contains only digits and optional plus sign
            if not re.match(r'^\+?\d{9,15}$', clean_phone):
                raise forms.ValidationError(
                    "Enter a valid phone number with 9-15 digits. "
                    "Format: +1234567890 or (123) 456-7890"
                )
        return phone

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()
            Student.objects.create(
                student=user,
                level=self.cleaned_data.get("level"),
                year=self.cleaned_data.get("year"),
                program=self.cleaned_data.get("program"),
            )

        return user


class ProfileUpdateForm(UserChangeForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )

    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "placeholder": "+1234567890 or (123) 456-7890",
                "pattern": r"^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
            }
        ),
        label="Phone No.",
        help_text="Enter phone number in format: +1234567890 or (123) 456-7890",
        required=False,
    )

    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address / city",
    )

    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            # Exclude current user from uniqueness check
            existing_users = User.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                existing_users = existing_users.exclude(pk=self.instance.pk)
            if existing_users.exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces, dashes, and parentheses for validation
            import re
            clean_phone = re.sub(r'[-.\s\(\)]', '', phone)
            # Check if it contains only digits and optional plus sign
            if not re.match(r'^\+?\d{9,15}$', clean_phone):
                raise forms.ValidationError(
                    "Enter a valid phone number with 9-15 digits. "
                    "Format: +1234567890 or (123) 456-7890"
                )
        return phone

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone",
            "address",
            "picture",
        ]


class ProgramUpdateForm(forms.ModelForm):
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Program",
    )

    class Meta:
        model = Student
        fields = ["program", "level", "year"]
        widgets = {
            "level": forms.Select(
                attrs={"class": "browser-default custom-select form-control"}
            ),
            "year": forms.Select(
                attrs={"class": "browser-default custom-select form-control"}
            ),
        }


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-mail address. "
            self.add_error("email", msg)
            return email


class ParentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Username",
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control",
                "placeholder": "+1234567890 or (123) 456-7890",
                "pattern": r"^(\+\d{1,3}[-.\s]?)?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$",
            }
        ),
        label="Mobile No.",
        help_text="Enter phone number in format: +1234567890 or (123) 456-7890",
        required=False,
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )

    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Student",
    )

    relation_ship = forms.CharField(
        widget=forms.Select(
            choices=RELATION_SHIP,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
    )

    # def validate_email(self):
    #     email = self.cleaned_data['email']
    #     if User.objects.filter(email__iexact=email, is_active=True).exists():
    #         raise forms.ValidationError("Email has taken, try another email address. ")

    def clean_email(self):
        """Validate email uniqueness and format"""
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
            if User.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email

    def clean_phone(self):
        """Validate phone number format"""
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces, dashes, and parentheses for validation
            import re
            clean_phone = re.sub(r'[-.\s\(\)]', '', phone)
            # Check if it contains only digits and optional plus sign
            if not re.match(r'^\+?\d{9,15}$', clean_phone):
                raise forms.ValidationError(
                    "Enter a valid phone number with 9-15 digits. "
                    "Format: +1234567890 or (123) 456-7890"
                )
        return phone

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        user.save()
        parent = Parent.objects.create(
            user=user,
            student=self.cleaned_data.get("student"),
            relation_ship=self.cleaned_data.get("relation_ship"),
        )
        parent.save()
        return user
