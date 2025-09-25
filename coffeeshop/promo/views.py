"""
Views for promo listing and promo application.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView
from promo.forms import ChoosePromoForm
from promo.models import Promo


class PromoListView(ListView):
    """
    View for listing all active promos.
    """

    model: type[Promo] = Promo
    template_name: str = "promo.html"
    context_object_name: str = "promo_list"


class PromoApplyView(View):
    """
    View for applying a selected promo code to the session.
    """

    @staticmethod
    def post(request: HttpRequest) -> HttpResponse:
        """
        Handle POST request to apply a promo code.
        """
        form: ChoosePromoForm = ChoosePromoForm(request.POST)
        if form.is_valid():
            promo: Promo = form.cleaned_data["active_promos"]
            request.session["applied_promo_id"] = promo.id
        return redirect("cart_detail")
