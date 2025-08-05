"""
Forms for order creation and validation.
"""

from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from order.models import Order


class OrderCreateForm(forms.ModelForm):
    """
    Form for creating an order based on the Order model.
    Adds custom validators and checks user authentication.
    """

    phone: forms.CharField = forms.CharField(
        max_length=20,
        label="Phone",
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s]{10,15}$", message="Phone number must be in format: '+999999999'. Up to 15 digits."
            )
        ],
    )

    delivery_address: forms.CharField = forms.CharField(
        label="Delivery Address",
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Street, house, apartment", "minlength": 10}),
        validators=[MinLengthValidator(10, message="Address must contain at least 10 characters")],
    )

    class Meta:
        model = Order
        fields = ["delivery_address", "phone"]

    def __init__(self, *args: object, user: User | None = None, **kwargs: object) -> None:
        """
        Initialize the order creation form.
        Args:
            *args: Positional arguments.
            user (User | None): The user placing the order.
            **kwargs: Keyword arguments.
        """
        self.user: User | None = user
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, object]:
        """
        Validates form data.
        Returns:
            dict[str, object]: Cleaned form data.
        Raises:
            ValidationError: If user is not authenticated or inactive.
        """
        cleaned_data: dict[str, object] = super().clean()
        if not self.user:
            raise ValidationError("You must be logged in to place an order.")
        if not self.user.is_active:
            raise ValidationError("Your account is inactive. Please contact support.")
        return cleaned_data
