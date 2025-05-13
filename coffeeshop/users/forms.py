from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import AbstractUser


class LoginUserForm(AuthenticationForm):
    """
    Custom authentication form that extends Django's built-in AuthenticationForm.

    Features:
    - Custom label for username field ('Login')
    - Password field with hidden input
    """

    username = forms.CharField(label="Login")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    class Meta:
        model: type[AbstractUser] = get_user_model()
        fields: list[str] = ["username", "password"]


class RegisterUserForm(UserCreationForm):
    """
    Custom user registration form that extends Django's UserCreationForm.

    Additional fields:
    - Email (required)
    - First name
    - Last name

    Custom validation:
    - Ensures email uniqueness
    """

    username = forms.CharField(label="Login")
    email = forms.EmailField(label="E-mail", required=True)
    first_name = forms.CharField(label="First Name", max_length=200)
    last_name = forms.CharField(label="Last Name", max_length=200)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput())

    class Meta:
        model: type[AbstractUser] = get_user_model()
        fields: list[str] = ["username", "email", "first_name", "last_name", "password1", "password2"]

    def clean_email(self) -> str:
        """
        Validate that the email is unique.

        Returns:
            str: The validated email address

        Raises:
            forms.ValidationError: If email already exists in database
        """
        email = self.cleaned_data["email"]
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email


class ProfileUserForm(forms.ModelForm):
    """
    Form for viewing and editing user profile information.

    Features:
    - Disabled username and email fields
    - Editable first and last name fields
    """

    username = forms.CharField(disabled=True, label="Login")
    email = forms.EmailField(disabled=True, label="E-mail")
    first_name = forms.CharField(label="First Name", max_length=200)
    last_name = forms.CharField(label="Last Name", max_length=200)

    class Meta:
        model: type[AbstractUser] = get_user_model()
        fields: list[str] = ["username", "email", "first_name", "last_name"]
