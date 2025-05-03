from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest


class EmailAuthBackend(BaseBackend):
    """
    Custom authentication backend that allows users to log in with their email address.

    This backend authenticates users by checking their email and password against
    the database. It extends Django's BaseBackend to provide custom authentication logic.
    """

    def authenticate(
        self, request: HttpRequest, username: str | None = None, password: str | None = None, **kwargs
    ) -> AbstractBaseUser | None:
        """
        Authenticate a user based on email address and password.

        Args:
            request: The HttpRequest object (unused in this implementation but required by interface)
            username: The email address to authenticate with (Django's auth system uses 'username' parameter)
            password: The password to verify
            **kwargs: Additional arguments (unused)

        Returns:
            The authenticated user object if credentials are valid, None otherwise
        """
        user_model: type[AbstractBaseUser] = get_user_model()
        try:
            user: AbstractBaseUser = user_model.objects.get(email=username)
            if user.check_password(password) and user.is_active:
                return user
            return None
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            return None

    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        """
        Retrieve a user from the database by their primary key.

        Args:
            user_id: The primary key (ID) of the user to retrieve

        Returns:
            The user object if found, None otherwise
        """
        user_model: type[AbstractBaseUser] = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except (user_model.DoesNotExist, ValueError, TypeError):
            return None
