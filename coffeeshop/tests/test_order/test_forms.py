from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from order.forms import OrderCreateForm


class TestOrderCreateForm:
    """Unit tests for OrderCreateForm validation and functionality."""

    def test_form_fields(self) -> None:
        """Test form fields presence and types.
        
        Verifies that:
        - Required fields are present
        - Field widgets have correct attributes
        """
        form = OrderCreateForm()
        assert 'phone' in form.fields
        assert 'delivery_address' in form.fields
        assert form.fields['delivery_address'].widget.attrs.get('rows') == 3
        assert form.fields['delivery_address'].widget.attrs.get('minlength') == 10

    def test_form_labels(self) -> None:
        """Test form field labels.
        
        Verifies that field labels are correctly set.
        """
        form = OrderCreateForm()
        assert form.fields['phone'].label == 'Phone'
        assert form.fields['delivery_address'].label == 'Delivery Address'

    @pytest.mark.parametrize('phone,is_valid', [
        ('+79001234567', True),
        ('+7 900 123 45 67', True),
        ('89001234567', True),
        ('123', False),
        ('abc', False),
        ('', False),
    ])
    def test_phone_validation(self, phone: str, is_valid: bool, test_user: User) -> None:
        """Test phone number validation.
        
        Args:
            phone: Phone number to test
            is_valid: Whether the phone number should be valid
            test_user: Test user fixture
        """
        form = OrderCreateForm(data={'phone': phone, 'delivery_address': 'Valid address' * 2}, user=test_user)
        assert form.is_valid() == is_valid
        if not is_valid:
            assert 'phone' in form.errors

    @pytest.mark.parametrize('address,is_valid', [
        ('123 Main Street, Apt 4B, City, 123456', True),
        ('Short', False),
        ('', False),
    ])
    def test_address_validation(self, address: str, is_valid: bool, test_user: User) -> None:
        """Test delivery address validation.
        
        Args:
            address: Address to test
            is_valid: Whether the address should be valid
            test_user: Test user fixture
        """
        form = OrderCreateForm(data={'phone': '+79001234567', 'delivery_address': address}, user=test_user)
        assert form.is_valid() == is_valid
        if not is_valid:
            assert 'delivery_address' in form.errors

    def test_form_with_valid_data(self, order_form_data: dict[str, str], test_user: User) -> None:
        """Test form with valid data.
        
        Args:
            order_form_data: Valid form data fixture
            test_user: Test user fixture
        """
        form = OrderCreateForm(data=order_form_data, user=test_user)
        assert form.is_valid()
        assert form.cleaned_data['phone'] == order_form_data['phone']
        assert form.cleaned_data['delivery_address'] == order_form_data['delivery_address']

    def test_form_with_invalid_data(self, invalid_order_form_data: dict[str, str], test_user: User) -> None:
        """Test form with invalid data.
        
        Args:
            invalid_order_form_data: Invalid form data fixture
            test_user: Test user fixture
        """
        form = OrderCreateForm(data=invalid_order_form_data, user=test_user)
        assert not form.is_valid()
        assert 'phone' in form.errors
        assert 'delivery_address' in form.errors

    def test_form_without_user(self, order_form_data: dict[str, str]) -> None:
        """Test form validation without user.
        
        Args:
            order_form_data: Valid form data fixture
        """
        form = OrderCreateForm(data=order_form_data)
        assert not form.is_valid()
        assert '__all__' in form.errors

    def test_form_with_inactive_user(self, order_form_data: dict[str, str], inactive_user: User) -> None:
        """Test form validation with inactive user.
        
        Args:
            order_form_data: Valid form data fixture
            inactive_user: Inactive user fixture
        """
        form = OrderCreateForm(data=order_form_data, user=inactive_user)
        assert not form.is_valid()
        assert '__all__' in form.errors

    def test_form_clean_method(self, order_form_data: dict[str, str], test_user: User, mock_order_form: None) -> None:
        """Test form clean method with mock.
        
        Args:
            order_form_data: Valid form data fixture
            test_user: Test user fixture
            mock_order_form: Mocked form fixture
        """
        form = OrderCreateForm(data=order_form_data, user=test_user)
        form.is_valid()
        cleaned_data = form.clean()
        assert cleaned_data == form.cleaned_data
