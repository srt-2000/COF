from __future__ import annotations

from typing import Any

from cart.factory import CartFactory
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import QuerySet
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView
from order.factory_order import OrderFactory
from order.forms import OrderCreateForm
from order.interfaces import OrderData, OrderItemData
from order.models import Order


class OrderCreateView(LoginRequiredMixin, FormView):
    """
    View for order creation:
    - Inherits from FormView for form handling
    - Uses LoginRequiredMixin for authentication check
    - Adds cart to context
    """

    form_class = OrderCreateForm
    template_name = "create_order.html"
    success_url = reverse_lazy("order_detail")
    order_data: OrderData

    def get_context_data(self, **kwargs: dict[str, object]) -> dict[str, Any]:
        """
        Add cart to context

        Returns:
            dict: Context with cart data
        """
        context = super().get_context_data(**kwargs)
        cart = CartFactory.create_from_request(self.request)
        context["cart"] = cart
        return context

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Add user to form

        Returns:
            dict: Form kwargs with user
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: OrderCreateForm) -> HttpResponse:
        """
        Handle valid form submission

        Args:
            form: Validated form instance

        Returns:
            HttpResponse: Redirect response
        """
        cart = CartFactory.create_from_request(self.request)

        # Prepare order items data
        items: list[OrderItemData] = [
            {
                "product_id": item["product"].id,
                "product_name": item["product"].name,
                "quantity": item["quantity"],
                "price": item["price"],
            }
            for item in cart
        ]

        # Create order through service
        order_service = OrderFactory.create_order_service()
        self.order_data = order_service.create_order(
            user=self.request.user,
            items=items,
            total_price=cart.get_total_price(),
            delivery_address=form.cleaned_data["delivery_address"],
            phone=form.cleaned_data["phone"],
        )

        # Clear cart
        cart.clear()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        """
        Get URL for redirect after successful order

        Returns:
            str: URL for order detail page
        """
        return reverse_lazy("order_detail", kwargs={"pk": self.order_data["order_id"]})

    def send_order_notification(self, order_data: OrderData) -> None:
        """
        Send order notification email

        Args:
            order_data: Order data for notification
        """
        try:
            subject = f"New Order #{order_data['order_id']}"
            message = render_to_string("order_notification.txt", {"order": order_data})
            html_message = render_to_string("order_notification.html", {"order": order_data})

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                html_message=html_message,
            )
        except Exception as e:
            messages.error(self.request, f"Error sending order notification: {e}")


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    View for order details:
    - Inherits from DetailView
    - Automatically gets order by pk
    - Filters only current user's orders
    """

    model = Order
    template_name = "order_created.html"
    context_object_name = "order"

    def get_queryset(self) -> QuerySet[Order]:
        """
        Limit access to user's own orders

        Returns:
            QuerySet: Filtered queryset of user's orders
        """
        return super().get_queryset().filter(user=self.request.user)
