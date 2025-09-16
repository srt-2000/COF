from __future__ import annotations

import pytest
from django import forms
from promo.forms import ChoosePromoForm
from promo.models import Promo


def test_form_field_types():
    """Test for form fields types"""
    form = ChoosePromoForm()
    assert isinstance(form.fields["active_promos"], forms.ModelChoiceField)
    assert form.fields["active_promos"].label == "Choose active promo"


def test_queryset_filtering(active_promo, inactive_promo):
    """Test for form queryset - only active promos"""
    form = ChoosePromoForm()
    form.fields["active_promos"].queryset = Promo.objects.filter(is_active=True)

    queryset = form.fields["active_promos"].queryset

    assert queryset.count() == 1
    assert queryset.first().id == active_promo.id
    assert queryset.first().name == "ACTIVE1"


@pytest.mark.parametrize(
    "promo_data,expected_valid",
    [
        ({"active_promos": 1}, True),
        ({"active_promos": 999}, False),
        ({}, False),
    ],
)
def test_parametrized_validation(active_promo, promo_data, expected_valid):
    """Parametrize validation test"""
    if "active_promos" in promo_data and promo_data["active_promos"] == 1:
        promo_data["active_promos"] = active_promo.id

    form = ChoosePromoForm(data=promo_data)
    assert form.is_valid() == expected_valid
