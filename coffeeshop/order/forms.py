from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator

from .models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Order creation form based on model:
    - Inherits from ModelForm
    - Adds custom validators
    - Checks user authentication
    """

    phone = forms.CharField(
        max_length=20,
        label="Phone",
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s]{10,15}$", message="Phone number must be in format: '+999999999'. Up to 15 digits."
            )
        ],
    )

    delivery_address = forms.CharField(
        label="Delivery Address",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Street, house, apartment", "minlength": 10}),
        validators=[MinLengthValidator(10, message="Address must contain at least 10 characters")],
    )

    class Meta:
        model = Order
        fields = ["delivery_address", "phone"]

    def __init__(self, *args: object, user: User | None = None, **kwargs: dict[str, object]) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        """
        Validates form data

        Returns:
            dict: Cleaned form data

        Raises:
            ValidationError: If user is not authenticated or inactive
        """
        cleaned_data = super().clean()
        if not self.user:
            raise ValidationError("You must be logged in to place an order.")
        if not self.user.is_active:
            raise ValidationError("Your account is inactive. Please contact support.")
        return cleaned_data
