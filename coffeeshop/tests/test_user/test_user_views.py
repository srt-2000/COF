from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user, get_user_model
from django.test import Client
from django.urls import reverse

if TYPE_CHECKING:
    from django.contrib.auth.models import User


# Unit tests
def test_login_user_view_get(client: Client) -> None:
    """Test GET request for login page.

    Args:
        client: Django test client instance.
    """
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200
    assert "login.html" in [t.name for t in response.templates]
    assert "Authorisation" in response.context["title"]


def test_register_user_view_get(client: Client) -> None:
    """Test GET request for registration page.

    Args:
        client: Django test client instance.
    """
    url = reverse("registration")
    response = client.get(url)
    assert response.status_code == 200
    assert "register.html" in [t.name for t in response.templates]
    assert "Registration" in response.context["title"]


def test_profile_user_view_get(client: Client, test_user: User) -> None:
    """Test GET request for profile page.

    Args:
        client: Django test client instance.
        test_user: Authenticated user instance for testing.
    """
    client.force_login(test_user)
    url = reverse("profile")
    response = client.get(url)
    assert response.status_code == 200
    assert "profile.html" in [t.name for t in response.templates]
    assert "Profile user" in response.context["title"]


# Integration tests
def test_login_user_view_post_success(client: Client, test_user: User) -> None:
    """Test successful login attempt.

    Args:
        client: Django test client instance.
        test_user: Existing user instance for testing.
    """
    url = reverse("login")
    data = {"username": test_user.email, "password": "existing123"}
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == "/"


def test_register_user_view_post_success(client: Client) -> None:
    """Test successful user registration.

    Args:
        client: Django test client instance.
    """
    url = reverse("registration")
    data = {
        "username": "newuser",
        "email": "newuser@test.com",
        "first_name": "New",
        "last_name": "User",
        "password1": "testpass123",
        "password2": "testpass123",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse("login")
    assert get_user_model().objects.filter(username="newuser").exists()


def test_profile_user_view_post_success(client: Client, test_user: User) -> None:
    """Test successful profile update.

    Args:
        client: Django test client instance.
        test_user: Authenticated user instance for testing.
    """
    client.force_login(test_user)
    url = reverse("profile")
    data = {"username": test_user.username, "email": test_user.email, "first_name": "Updated", "last_name": "Name"}
    response = client.post(url, data)
    assert response.status_code == 302
    # Check redirect to profile without checking arguments
    assert response.url.startswith("/users/profile/")
    test_user.refresh_from_db()
    assert test_user.first_name == "Updated"
    assert test_user.last_name == "Name"


# Parameterized tests
@pytest.mark.parametrize(
    "invalid_data,expected_errors",
    [
        ({"username": "", "password": "testpass123"}, ["This field is required."]),
        ({"username": "test@test.com", "password": ""}, ["This field is required."]),
        ({"username": "wrong@test.com", "password": "testpass123"}, ["Please enter a correct username and password."]),
    ],
)
def test_login_user_view_post_invalid(client: Client, invalid_data: dict[str, str], expected_errors: list[str]) -> None:
    """Test failed login attempts with various invalid data.

    Args:
        client: Django test client instance.
        invalid_data: Dictionary with invalid form data.
        expected_errors: List of expected error messages.
    """
    url = reverse("login")
    response = client.post(url, invalid_data)

    assert response.status_code == 200, "Expected status 200 for invalid data"
    assert "form" in response.context, "Form not found in context"

    form = response.context["form"]
    for error in expected_errors:
        assert error in str(form.errors), f"Expected error: '{error}'"

    assert not get_user(client).is_authenticated, "User should not be authenticated"
    assert b"<form" in response.content, "Form not rendered in response"


# Tests with mocks
@patch("users.authentication.EmailAuthBackend.authenticate")
def test_login_user_view_post_mock_auth(mock_authenticate: MagicMock, client: Client) -> None:
    """Test login with mocked email authentication.

    Args:
        mock_authenticate: Mocked authenticate method.
        client: Django test client instance.
    """
    mock_authenticate.return_value = None
    url = reverse("login")
    data = {"username": "test@test.com", "password": "testpass123"}
    response = client.post(url, data)
    assert response.status_code == 200
    mock_authenticate.assert_called_once()


# Tests for redirects
def test_profile_user_view_redirect_if_not_logged_in(client: Client) -> None:
    """Test redirect for unauthorized users.

    Args:
        client: Django test client instance.
    """
    url = reverse("profile")
    response = client.get(url)
    assert response.status_code == 302
    login_url = reverse("login")
    assert response.url.startswith(login_url)
    assert "next=" in response.url
    assert "profile/" in response.url  # Check only base URL
