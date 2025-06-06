from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Model, QuerySet
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import LoginUserForm, ProfileUserForm, RegisterUserForm


class LoginUser(LoginView):
    """
    View for handling user authentication.

    Inherits from Django's built-in LoginView and customizes the form,
    template, and page title for the login page.
    """

    form_class: type[LoginUserForm] = LoginUserForm
    template_name: str = "login.html"
    extra_context: dict[str, str] = {"title": "Authorisation"}


class RegisterUser(CreateView):
    """
    View for handling new user registration.

    Provides a form for new users to create an account and redirects
    to the login page upon successful registration.
    """

    form_class: type[RegisterUserForm] = RegisterUserForm
    template_name: str = "register.html"
    extra_context: dict[str, str] = {"title": "Registration"}
    success_url: str = reverse_lazy("login")


class ProfileUser(LoginRequiredMixin, UpdateView):
    """
    View for displaying and updating user profile information.

    Requires authentication and allows users to update their profile details.
    Automatically uses the currently logged-in user's profile.
    """

    model: type[Model] = get_user_model()
    form_class: type[ProfileUserForm] = ProfileUserForm
    template_name: str = "profile.html"
    extra_context: dict[str, str] = {"title": "Profile user"}

    def get_success_url(self) -> str:
        """
        Return the URL to redirect to after successful profile update.

        Returns:
            The URL for the profile page as a string
        """
        return reverse_lazy("profile")

    def get_object(self, queryset: QuerySet | None = None) -> Model:
        """
        Get the user object to be edited in the profile view.

        Args:
            queryset: Optional queryset to filter the objects (not used in this case)

        Returns:
            The currently authenticated user object
        """
        return self.request.user