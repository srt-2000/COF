"""
Views for the cart application.

This module provides class-based views for cart detail, add, update, remove, and clear actions.
"""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from catalog.models import Product
from cart.factory import CartFactory
from cart.cart import Cart


class CartDetailView(View):
    """
    View to display the cart details.
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        cart: Cart = CartFactory.create_from_request(request)
        return render(request, 'cart_detail.html', {'cart': cart})


class CartAddView(View):
    """
    View to add a product to the cart.
    """
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        cart: Cart = CartFactory.create_from_request(request)
        product: Product = get_object_or_404(Product, id=product_id)
        quantity: int = int(request.POST.get('quantity', 1))
        cart.add(product.id, quantity)
        return redirect(request.META.get('HTTP_REFERER', '/'))


class CartUpdateView(View):
    """
    View to update the quantity of a product in the cart.
    """
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        cart: Cart = CartFactory.create_from_request(request)
        product: Product = get_object_or_404(Product, id=product_id)
        quantity: int = int(request.POST.get('quantity', 1))
        cart.add(product.id, quantity, override_quantity=True)
        return redirect('cart_detail')


class CartRemoveView(View):
    """
    View to remove a product from the cart.
    """
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        cart: Cart = CartFactory.create_from_request(request)
        product: Product = get_object_or_404(Product, id=product_id)
        cart.remove(product.id)
        return redirect('cart_detail')


class CartClearView(View):
    """
    View to clear all items from the cart.
    """
    def post(self, request: HttpRequest) -> HttpResponse:
        cart: Cart = CartFactory.create_from_request(request)
        cart.clear()
        return redirect('cart_detail')