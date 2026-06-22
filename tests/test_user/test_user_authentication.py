from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from coffeeshop.users.authentication import EmailAuthBackend

if TYPE_CHECKING:
    from django.contrib.auth.models import User
else:
    User = get_user_model()  # Runtime import


# Unit tests with mocks
@patch.object(User, "objects")
def test_authenticate_success(mock_objects: MagicMock, backend: EmailAuthBackend) -> None:
    """Test successful authentication with correct credentials."""
    mock_user = MagicMock()
    mock_user.check_password.return_value = True
    mock_objects.get.return_value = mock_user

    result = backend.authenticate(None, username="test@example.com", password="valid")
    assert result == mock_user
    mock_objects.get.assert_called_once_with(email="test@example.com")
    mock_user.check_password.assert_called_once_with("valid")


@patch.object(User, "objects")
def test_authenticate_wrong_password(mock_objects: MagicMock, backend: EmailAuthBackend) -> None:
    """Test authentication fails with incorrect password."""
    mock_user = MagicMock()
    mock_user.check_password.return_value = False
    mock_objects.get.return_value = mock_user

    result = backend.authenticate(None, username="test@example.com", password="invalid")
    assert result is None


@patch.object(User, "objects")
def test_authenticate_user_not_found(mock_objects: MagicMock, backend: EmailAuthBackend) -> None:
    """Test authentication fails when user does not exist."""
    mock_objects.get.side_effect = User.DoesNotExist

    result = backend.authenticate(None, username="nonexistent@example.com", password="any")
    assert result is None


@patch.object(User, "objects")
def test_authenticate_multiple_users(mock_objects: MagicMock, backend: EmailAuthBackend) -> None:
    """Test authentication fails when multiple users with same email exist."""
    mock_objects.get.side_effect = User.MultipleObjectsReturned

    result = backend.authenticate(None, username="duplicate@example.com", password="any")
    assert result is None


@patch.object(User, "objects")
def test_get_user_exists(mock_objects: MagicMock, backend: EmailAuthBackend) -> None:
    """Test retrieving an existing user by ID."""
    mock_user = MagicMock()
    mock_objects.get.return_value = mock_user

    result = backend.get_user(1)
    assert result == mock_user
    mock_objects.get.assert_called_once_with(pk=1)


@patch.object(User, "objects")
def test_get_user_not_exists(mock_objects: MagicMock, backend: EmailAuthBackend) -> None:
    """Test retrieving a non-existent user returns None."""
    mock_objects.get.side_effect = User.DoesNotExist

    result = backend.get_user(999)
    assert result is None


# Integration tests
def test_authenticate_success_integration(backend: EmailAuthBackend, user_with_email: User) -> None:
    """Test successful authentication with real database user."""
    authenticated_user = backend.authenticate(None, username="auth@example.com", password="secure123")
    assert authenticated_user == user_with_email


def test_authenticate_wrong_password_integration(backend: EmailAuthBackend, user_with_email: User) -> None:
    """Test authentication fails with wrong password (DB integration)."""
    assert backend.authenticate(None, username="auth@example.com", password="wrong") is None


def test_authenticate_user_not_found_integration(backend: EmailAuthBackend, user_with_email: User) -> None:
    """Test authentication fails for non-existent email (DB integration)."""
    assert backend.authenticate(None, username="nonexistent@example.com", password="any") is None


def test_get_user_exists_integration(backend: EmailAuthBackend, user_with_email: User) -> None:
    """Test retrieving existing user from database."""
    assert backend.get_user(user_with_email.pk) == user_with_email


def test_get_user_not_exists_integration(backend: EmailAuthBackend) -> None:
    """Test retrieving non-existent user from database returns None."""
    assert backend.get_user(999) is None


def test_authenticate_inactive_user(backend: EmailAuthBackend, inactive_user: User) -> None:
    """Test authentication fails for inactive users."""
    assert backend.authenticate(None, username="inactive@example.com", password="inactive123") is None


# Parameterized tests
@pytest.mark.parametrize(
    "email,password,expected",
    [
        ("auth@example.com", "secure123", True),  # correct credentials
        ("auth@example.com", "wrong", False),  # wrong password
        ("nonexistent@example.com", "any", False),  # non-existent email
        ("", "secure123", False),  # empty email
        ("auth@example.com", "", False),  # empty password
    ],
)
def test_authenticate_parameters(
    backend: EmailAuthBackend, user_with_email: User, email: str, password: str, expected: bool
) -> None:
    """Test authentication with various input combinations."""
    result = backend.authenticate(None, username=email, password=password)
    assert (result is not None) == expected


def test_get_user_existing(backend: EmailAuthBackend, user_with_email: User) -> None:
    """Test getting existing user."""
    result = backend.get_user(user_with_email.id)
    assert result is not None
    assert result == user_with_email


def test_get_user_nonexistent(backend: EmailAuthBackend) -> None:
    """Test getting non-existent user."""
    result = backend.get_user(999)
    assert result is None


def test_get_user_none(backend: EmailAuthBackend) -> None:
    """Test getting user with None ID."""
    result = backend.get_user(None)
    assert result is None


def test_get_user_string_id(backend: EmailAuthBackend) -> None:
    """Test getting user with string ID."""
    result = backend.get_user("abc")
    assert result is None
