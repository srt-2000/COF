"""
Views for the cart application.
"""

from __future__ import annotations

from cart.cart import Cart
from cart.factory import CartFactory
from catalog.models import Product
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from promo.forms import ChoosePromoForm


class CartDetailView(View):
    """
    View to display the cart details.
    """

    @staticmethod
    def get(request: HttpRequest) -> HttpResponse:
        """
        Handle GET request for cart details.
        Args:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponse: The rendered cart detail page.
        """

        choose_promo_form: ChoosePromoForm = ChoosePromoForm()
        return render(
            request,
            "cart_detail.html",
            {
                "promo_form": choose_promo_form,
            },
        )


class CartAddView(View):
    """
    View to add a product to the cart.
    """

    @staticmethod
    def post(request: HttpRequest, product_id: int) -> HttpResponse:
        """
        Handle POST request to add a product to the cart.
        Args:
            request (HttpRequest): The HTTP request object.
            product_id (int): The ID of the product to add.
        Returns:
            HttpResponse: Redirects to the previous page or home.
        """
        cart: Cart = CartFactory.create_from_session(request.session)
        product: Product = get_object_or_404(Product, id=product_id)
        quantity: int = int(request.POST.get("quantity", 1))
        cart.add(product.id, quantity) 

        request.session.pop("applied_promo_id", None)

        return redirect(request.META.get("HTTP_REFERER", "/"))


class CartUpdateView(View):
    """
    View to update the quantity of a product in the cart.
    """

    @staticmethod
    def post(request: HttpRequest, product_id: int) -> HttpResponse:
        """
        Handle POST request to update the quantity of a product in the cart.
        Args:
            request (HttpRequest): The HTTP request object.
            product_id (int): The ID of the product to update.
        Returns:
            HttpResponse: Redirects to the cart detail page.
        """
        cart: Cart = CartFactory.create_from_session(request.session)
        product: Product = get_object_or_404(Product, id=product_id)
        quantity: int = int(request.POST.get("quantity", 1))
        cart.add(product.id, quantity, override_quantity=True)

        request.session.pop("applied_promo_id", None)

        return redirect("cart_detail")


class CartRemoveView(View):
    """
    View to remove a product from the cart.
    """

    @staticmethod
    def post(request: HttpRequest, product_id: int) -> HttpResponse:
        """
        Handle POST request to remove a product from the cart.
        Args:
            request (HttpRequest): The HTTP request object.
            product_id (int): The ID of the product to remove.
        Returns:
            HttpResponse: Redirects to the cart detail page.
        """
        cart: Cart = CartFactory.create_from_session(request.session)
        product: Product = get_object_or_404(Product, id=product_id)
        cart.remove(product.id)

        request.session.pop("applied_promo_id", None)

        return redirect("cart_detail")


class CartClearView(View):
    """
    View to clear all items from the cart.
    """

    @staticmethod
    def post(request: HttpRequest) -> HttpResponse:
        """
        Handle POST request to clear the cart.
        Args:
            request (HttpRequest): The HTTP request object.
        Returns:
            HttpResponse: Redirects to the cart detail page.
        """
        cart: Cart = CartFactory.create_from_session(request.session)
        cart.clear()

        request.session.pop("applied_promo_id", None)

        return redirect("cart_detail")
