"""
Views for order creation, order details, and order notification logic.
"""

from __future__ import annotations

from cart.cart import Cart
from cart.factory import CartFactory
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView
from order.domains import OrderData
from order.factory_order import OrderFactory
from order.forms import OrderCreateForm
from order.models import Order


class OrderCreateView(LoginRequiredMixin, FormView):
    """
    View for order creation. Handles form validation, order creation, and notification.
    """

    form_class: type[OrderCreateForm] = OrderCreateForm
    template_name: str = "create_order.html"
    success_url: str = reverse_lazy("order_detail")
    order_data: OrderData

    def get_form_kwargs(self) -> dict[str, object]:
        """
        Add user to form.
        Returns:
            dict[str, object]: Form kwargs with user.
        """
        kwargs: dict[str, object] = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: OrderCreateForm) -> HttpResponse:
        """
        Handle valid form submission.
        Args:
            form (OrderCreateForm): Validated form instance.
        Returns:
            HttpResponse: Redirect response.
        """
        cart: Cart = CartFactory.create_from_session(self.request.session)
        applied_promo_id: int | None = self.request.session.get("applied_promo_id")

        order_service = OrderFactory.create_order_service()

        assert isinstance(self.request.user, User)

        self.order_data = order_service.create_order(
            user=self.request.user,
            cart=cart,
            form_data=form.cleaned_data,
            applied_promo_id=applied_promo_id,
        )

        order_id = self.order_data["order_id"]
        order_service.notifier.send_order_notification(order_id)

        cart.clear()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Get URL for redirect after successful order.
        Returns:
            str: URL for order detail page.
        """
        return reverse_lazy("order_detail", kwargs={"pk": self.order_data["order_id"]})


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    View for order details. Shows details for a specific order belonging to the current user.
    """

    model: type[Order] = Order
    template_name: str = "order_created.html"
    context_object_name: str = "order"

    def get_queryset(self) -> QuerySet[Order]:
        """
        Limit access to user's own orders.
        Returns:
            QuerySet[Order]: Filtered queryset of user's orders.
        """
        return super().get_queryset().filter(user=self.request.user)
