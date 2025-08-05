"""
Forms for promo selection and application.
"""
from __future__ import annotations

from django import forms
from promo.models import Promo


class ChoosePromoForm(forms.Form):
    """
    Form for choosing an active promo code.
    """

    active_promos: forms.ModelChoiceField = forms.ModelChoiceField(
        queryset=Promo.objects.filter(is_active=True), label="Choose active promo"
    )
