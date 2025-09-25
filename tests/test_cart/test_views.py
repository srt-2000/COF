"""
Tests for cart views.
"""

from __future__ import annotations

import pytest
from cart.factory import CartFactory
from cart.views import CartAddView, CartClearView, CartDetailView, CartRemoveView, CartUpdateView
from catalog.models import Product
from django.http import HttpRequest
from django.test import Client


class TestCartDetailView:
    """Tests for CartDetailView."""

    def test_get(
        self,
        mock_request: HttpRequest,
        mock_cart_factory: None,
        mock_render,
    ) -> None:
        """Test GET request for cart details.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
            mock_render: Mocked render function
        """
        view = CartDetailView()
        response = view.get(mock_request)

        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        assert args[0] == mock_request
        assert args[1] == "cart_detail.html"
        assert "promo_form" in args[2]
        assert response == mock_render.return_value


class TestCartAddView:
    """Tests for CartAddView."""

    @pytest.mark.parametrize(
        "quantity,override_quantity",
        [
            (1, False),  # Default quantity
            (2, False),  # Custom quantity
            (3, True),  # Override quantity
        ],
    )
    def test_post(
        self,
        mock_request: HttpRequest,
        mock_cart_factory: None,
        mock_get_object_or_404,
        mock_redirect,
        product_object_tea: Product,
        quantity: int,
        override_quantity: bool,
    ) -> None:
        """Test POST request to add product to cart.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
            mock_get_object_or_404: Mocked get_object_or_404 function
            mock_redirect: Mocked redirect function
            product_object_tea: Tea product instance
            quantity: Product quantity
            override_quantity: Whether to override existing quantity
        """
        mock_request.POST = {"quantity": str(quantity)}
        mock_request.META = {"HTTP_REFERER": "/test/"}

        mock_get_object_or_404.return_value = product_object_tea

        view = CartAddView()
        response = view.post(mock_request, product_object_tea.id)

        CartFactory.create_from_session.assert_called_once_with(mock_request.session)
        mock_get_object_or_404.assert_called_once_with(Product, id=product_object_tea.id)

        cart = CartFactory.create_from_session.return_value
        cart.add.assert_called_once_with(product_object_tea.id, quantity)

        mock_redirect.assert_called_once_with("/test/")
        assert response == mock_redirect.return_value


class TestCartUpdateView:
    """Tests for CartUpdateView."""

    @pytest.mark.parametrize(
        "quantity",
        [1, 2, 3],
    )
    def test_post(
        self,
        mock_request: HttpRequest,
        mock_cart_factory: None,
        mock_get_object_or_404,
        mock_redirect,
        product_object_tea: Product,
        quantity: int,
    ) -> None:
        """Test POST request to update product quantity in cart.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
            mock_get_object_or_404: Mocked get_object_or_404 function
            mock_redirect: Mocked redirect function
            product_object_tea: Tea product instance
            quantity: New product quantity
        """
        mock_request.POST = {"quantity": str(quantity)}
        mock_get_object_or_404.return_value = product_object_tea

        view = CartUpdateView()
        response = view.post(mock_request, product_object_tea.id)

        CartFactory.create_from_session.assert_called_once_with(mock_request.session)
        mock_get_object_or_404.assert_called_once_with(Product, id=product_object_tea.id)

        cart = CartFactory.create_from_session.return_value
        cart.add.assert_called_once_with(product_object_tea.id, quantity, override_quantity=True)

        mock_redirect.assert_called_once_with("cart_detail")
        assert response == mock_redirect.return_value


class TestCartRemoveView:
    """Tests for CartRemoveView."""

    def test_post(
        self,
        mock_request: HttpRequest,
        mock_cart_factory: None,
        mock_get_object_or_404,
        mock_redirect,
        product_object_tea: Product,
    ) -> None:
        """Test POST request to remove product from cart.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
            mock_get_object_or_404: Mocked get_object_or_404 function
            mock_redirect: Mocked redirect function
            product_object_tea: Tea product instance
        """
        mock_get_object_or_404.return_value = product_object_tea

        view = CartRemoveView()
        response = view.post(mock_request, product_object_tea.id)

        CartFactory.create_from_session.assert_called_once_with(mock_request.session)
        mock_get_object_or_404.assert_called_once_with(Product, id=product_object_tea.id)

        cart = CartFactory.create_from_session.return_value
        cart.remove.assert_called_once_with(product_object_tea.id)

        mock_redirect.assert_called_once_with("cart_detail")
        assert response == mock_redirect.return_value


class TestCartClearView:
    """Tests for CartClearView."""

    def test_post(
        self,
        mock_request: HttpRequest,
        mock_cart_factory: None,
        mock_redirect,
    ) -> None:
        """Test POST request to clear cart.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
            mock_redirect: Mocked redirect function
        """
        view = CartClearView()
        response = view.post(mock_request)

        CartFactory.create_from_session.assert_called_once_with(mock_request.session)

        cart = CartFactory.create_from_session.return_value
        cart.clear.assert_called_once()

        mock_redirect.assert_called_once_with("cart_detail")
        assert response == mock_redirect.return_value
