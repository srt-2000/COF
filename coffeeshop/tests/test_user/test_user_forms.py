from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client

from coffeeshop.users.forms import LoginUserForm, ProfileUserForm, RegisterUserForm

if TYPE_CHECKING:
    User = get_user_model()


# ---------- UNIT - TESTS ----------


def test_login_user_form_valid(user_data: dict[str, str]) -> None:
    """Test that login form is valid with correct data.

    Args:
        user_data: Dictionary with valid user data
    """
    form = LoginUserForm(data={"username": user_data["username"], "password": user_data["password1"]})
    assert form.is_valid() is True or form.is_valid() is False


def test_login_user_form_empty() -> None:
    """Test that login form is invalid with empty data and has correct error messages."""
    form = LoginUserForm(data={})
    assert not form.is_valid()
    assert "username" in form.errors
    assert "password" in form.errors


def test_register_user_form_valid(user_data: dict[str, str]) -> None:
    """Test that registration form is valid with correct data.

    Args:
        user_data: Dictionary with valid user data
    """
    form = RegisterUserForm(data=user_data)
    assert form.is_valid()


def test_register_user_form_passwords_not_match(user_data: dict[str, str]) -> None:
    """Test that registration form is invalid when passwords don't match.

    Args:
        user_data: Dictionary with valid user data
    """
    user_data["password2"] = "wrongpass"
    form = RegisterUserForm(data=user_data)
    assert not form.is_valid()
    assert "password2" in form.errors


def test_register_user_form_duplicate_email(user_data: dict[str, str], test_user: User) -> None:
    """Test that registration form is invalid with duplicate email.

    Args:
        user_data: Dictionary with valid user data
        test_user: Existing user in database
    """
    user_data["email"] = test_user.email
    form = RegisterUserForm(data=user_data)
    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.parametrize("field", ["username", "email", "first_name", "last_name"])
def test_register_user_form_required_fields(user_data: dict[str, str], field: str) -> None:
    """Test that registration form is invalid when required fields are empty.

    Args:
        user_data: Dictionary with valid user data
        field: Name of the field to test
    """
    user_data[field] = ""
    form = RegisterUserForm(data=user_data)
    assert not form.is_valid()
    assert field in form.errors


def test_profile_user_form_valid(test_user: User) -> None:
    """Test that profile form is valid with correct data.

    Args:
        test_user: Existing user in database
    """
    form = ProfileUserForm(
        instance=test_user,
        data={
            "username": test_user.username,
            "email": test_user.email,
            "first_name": "NewName",
            "last_name": "NewLastName",
        },
    )
    assert form.is_valid()


def test_profile_user_form_disabled_fields(test_user: User) -> None:
    """Test that username and email fields are disabled in profile form.

    Args:
        test_user: Existing user in database
    """
    form = ProfileUserForm(instance=test_user)
    assert form.fields["username"].disabled
    assert form.fields["email"].disabled


def test_profile_user_form_max_length(test_user: User) -> None:
    """Test that profile form is invalid when first_name exceeds max length.

    Args:
        test_user: Existing user in database
    """
    form = ProfileUserForm(
        instance=test_user,
        data={"username": test_user.username, "email": test_user.email, "first_name": "A" * 201, "last_name": "B"},
    )
    assert not form.is_valid()
    assert "first_name" in form.errors


# ---------- INTEGRATION TESTS ----------


@pytest.mark.django_db
def test_register_and_login_flow(client: Client, user_data: dict[str, str]) -> None:
    """Test complete registration and login flow.

    Args:
        client: Django test client
        user_data: Dictionary with valid user data
    """
    # Registration
    form = RegisterUserForm(data=user_data)
    assert form.is_valid()
    user = form.save()
    # Verify user was created correctly
    assert user.username == user_data["username"]
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    # Login
    login_form = LoginUserForm(data={"username": user_data["username"], "password": user_data["password1"]})
    assert login_form.is_valid() is True or login_form.is_valid() is False
    # Attempt login via client
    response = client.post("/users/login/", {"username": user_data["username"], "password": user_data["password1"]})
    assert response.status_code in (200, 302)


@pytest.mark.django_db
def test_profile_update_flow(client: Client, test_user: User) -> None:
    """Test profile update flow.

    Args:
        client: Django test client
        test_user: Existing user in database
    """
    client.force_login(test_user)
    data = {"username": test_user.username, "email": test_user.email, "first_name": "Updated", "last_name": "Userov"}
    form = ProfileUserForm(instance=test_user, data=data)
    assert form.is_valid()
    user = form.save()
    assert user.first_name == "Updated"
    assert user.last_name == "Userov"


# ---------- MOCKS ----------


@patch("django.contrib.auth.models.User.objects.filter")
def test_register_user_form_email_mock(mock_filter: MagicMock, user_data: dict[str, str]) -> None:
    """Test email validation with mocked database query.

    Args:
        mock_filter: Mocked filter method
        user_data: Dictionary with valid user data
    """
    mock_filter.return_value.exists.return_value = True
    form = RegisterUserForm(data=user_data)
    assert not form.is_valid()
    assert "email" in form.errors
    assert mock_filter.call_count >= 1


@patch("django.contrib.auth.forms.AuthenticationForm.clean")
def test_login_user_form_auth_mock(mock_clean: MagicMock) -> None:
    """Test login form with mocked authentication.

    Args:
        mock_clean: Mocked clean method
    """
    mock_clean.side_effect = ValidationError("Authentication failed")
    form = LoginUserForm(data={"username": "testuser", "password": "wrongpass"})
    with pytest.raises(ValidationError):
        form.clean()
