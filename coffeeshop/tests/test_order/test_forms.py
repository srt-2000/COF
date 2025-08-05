"""
Tests for order forms.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from order.forms import OrderCreateForm


class TestOrderCreateForm:
    """Tests for OrderCreateForm."""

    def test_form_fields(self) -> None:
        """Test that form has correct fields."""
        form = OrderCreateForm()
        
        assert 'delivery_address' in form.fields
        assert 'phone' in form.fields
        assert form.fields['delivery_address'].widget.__class__.__name__ == 'Textarea'
        assert form.fields['phone'].max_length == 20

    def test_form_with_user(self, test_user: User) -> None:
        """Test OrderCreateForm with user parameter."""
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B',
            'phone': '+79001234567'
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert form.is_valid()
        assert form.user == test_user

    def test_form_without_user(self) -> None:
        """Test OrderCreateForm without user parameter."""
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B',
            'phone': '+79001234567'
        }
        
        form = OrderCreateForm(data=form_data)
        assert not form.is_valid()
        assert 'You must be logged in to place an order.' in str(form.errors)

    def test_form_with_inactive_user(self, test_user: User) -> None:
        """Test OrderCreateForm with inactive user."""
        test_user.is_active = False
        test_user.save()
        
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B',
            'phone': '+79001234567'
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'Your account is inactive' in str(form.errors)

    @pytest.mark.parametrize('invalid_phone', [
        '123',  # Too short
        'abcdefghij',  # Non-numeric
        '+1234567890123456',  # Too long
    ])
    def test_invalid_phone_format(self, test_user: User, invalid_phone: str) -> None:
        """Test form validation with invalid phone formats."""
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B',
            'phone': invalid_phone
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'phone' in form.errors

    def test_short_delivery_address(self, test_user: User) -> None:
        """Test form validation with short delivery address."""
        form_data = {
            'delivery_address': 'Short',  # Less than 10 characters
            'phone': '+79001234567'
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert not form.is_valid()
        assert 'delivery_address' in form.errors

    def test_valid_form_data(self, test_user: User) -> None:
        """Test form validation with valid data."""
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B, City, 123456',
            'phone': '+79001234567'
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert form.is_valid()
        assert form.cleaned_data['delivery_address'] == form_data['delivery_address']
        assert form.cleaned_data['phone'] == form_data['phone']

    def test_form_initialization(self, test_user: User) -> None:
        """Test form initialization with user parameter."""
        form = OrderCreateForm(user=test_user)
        assert form.user == test_user

    def test_form_cleaned_data_structure(self, test_user: User) -> None:
        """Test that cleaned_data has correct structure."""
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B, City, 123456',
            'phone': '+79001234567'
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert form.is_valid()
        
        cleaned_data = form.cleaned_data
        assert 'delivery_address' in cleaned_data
        assert 'phone' in cleaned_data
        assert isinstance(cleaned_data['delivery_address'], str)
        assert isinstance(cleaned_data['phone'], str)

    def test_form_validation_error_messages(self, test_user: User) -> None:
        """Test that form provides meaningful error messages."""
        # Test with missing required fields
        form = OrderCreateForm(data={}, user=test_user)
        assert not form.is_valid()
        assert 'delivery_address' in form.errors
        assert 'phone' in form.errors

    def test_form_widget_attributes(self) -> None:
        """Test that form widgets have correct attributes."""
        form = OrderCreateForm()
        
        # Test delivery_address widget
        delivery_widget = form.fields['delivery_address'].widget
        assert delivery_widget.attrs.get('rows') == 3
        assert delivery_widget.attrs.get('placeholder') == 'Street, house, apartment'
        assert delivery_widget.attrs.get('minlength') == 10

    def test_form_phone_validator(self, test_user: User) -> None:
        """Test phone number validation."""
        valid_phones = [
            '+79001234567',
            '+7 900 123 45 67',
            '79001234567',
            '+12345678901'
        ]
        
        for phone in valid_phones:
            form_data = {
                'delivery_address': '123 Main Street, Apt 4B',
                'phone': phone
            }
            form = OrderCreateForm(data=form_data, user=test_user)
            assert form.is_valid(), f"Phone {phone} should be valid"

    def test_form_delivery_address_validator(self, test_user: User) -> None:
        """Test delivery address validation."""
        valid_addresses = [
            '123 Main Street, Apt 4B, City, 123456',
            'ул. Пушкина, д. 10, кв. 5, Москва, 123456',
            'Street Address, Building 1, Apartment 2, City, Postal Code'
        ]
        
        for address in valid_addresses:
            form_data = {
                'delivery_address': address,
                'phone': '+79001234567'
            }
            form = OrderCreateForm(data=form_data, user=test_user)
            assert form.is_valid(), f"Address '{address}' should be valid"

    def test_form_bound_unbound(self, test_user: User) -> None:
        """Test form bound and unbound states."""
        # Unbound form
        form = OrderCreateForm(user=test_user)
        assert not form.is_bound
        
        # Bound form with data
        form_data = {
            'delivery_address': '123 Main Street, Apt 4B',
            'phone': '+79001234567'
        }
        form = OrderCreateForm(data=form_data, user=test_user)
        assert form.is_bound

    def test_form_error_handling(self, test_user: User) -> None:
        """Test form error handling and display."""
        # Test with completely invalid data
        form_data = {
            'delivery_address': 'Short',
            'phone': 'invalid'
        }
        
        form = OrderCreateForm(data=form_data, user=test_user)
        assert not form.is_valid()
        
        # Check that errors are present
        assert 'delivery_address' in form.errors
        assert 'phone' in form.errors
        
        # Check that error messages are strings
        for field_errors in form.errors.values():
            for error in field_errors:
                assert isinstance(error, str)
