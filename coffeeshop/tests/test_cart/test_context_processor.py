"""Tests for cart context processor.

This module contains tests for the cart context processor functionality including:
- Tests for CartContext TypedDict structure
- Tests for cart context processor with mock and real requests
- Integration tests for cart context processor
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from cart.context_processor import CartContext, cart
from django.http import HttpRequest


class TestCartContext:
    """Tests for CartContext TypedDict."""

    def test_cart_context_structure(self) -> None:
        """Test CartContext structure.

        Verifies that CartContext contains a cart key with a MagicMock value.
        """
        context: CartContext = {"cart": MagicMock()}
        assert "cart" in context
        assert isinstance(context["cart"], MagicMock)


class TestCartContextProcessor:
    """Tests for cart context processor."""

    def test_cart_context_processor(self, mock_request: HttpRequest, mock_cart_factory: MagicMock) -> None:
        """Test cart context processor with mock request.

        Args:
            mock_request: Mocked HTTP request
            mock_cart_factory: Mocked cart factory
        """
        result = cart(mock_request)

        assert isinstance(result, dict)
        assert "cart" in result
        assert result["cart"] == mock_cart_factory.return_value
        mock_cart_factory.assert_called_once_with(mock_request)

    def test_cart_context_processor_with_real_request(self, mock_cart_factory: MagicMock) -> None:
        """Test cart context processor with real request object.

        Args:
            mock_cart_factory: Mocked cart factory
        """
        request = HttpRequest()
        request.session = {}

        result = cart(request)

        assert isinstance(result, dict)
        assert "cart" in result
        assert result["cart"] == mock_cart_factory.return_value
        mock_cart_factory.assert_called_once_with(request)


class TestCartContextProcessorIntegration:
    """Integration tests for cart context processor."""

    def test_cart_context_processor_integration(self, mock_request: HttpRequest) -> None:
        """Test cart context processor integration with CartFactory.

        Args:
            mock_request: Mocked HTTP request
        """
        with patch("cart.context_processor.CartFactory") as mock_factory:
            mock_cart = MagicMock()
            mock_factory.create_from_request.return_value = mock_cart

            result = cart(mock_request)

            assert isinstance(result, dict)
            assert "cart" in result
            assert result["cart"] == mock_cart
            mock_factory.create_from_request.assert_called_once_with(mock_request)

    def test_cart_context_processor_with_session(self, mock_cart_factory: MagicMock) -> None:
        """Test cart context processor with session data.

        Args:
            mock_cart_factory: Mocked cart factory
        """
        request = HttpRequest()
        request.session = {"cart": {"1": {"quantity": 2, "price": "100.00"}}}

        result = cart(request)

        assert isinstance(result, dict)
        assert "cart" in result
        assert result["cart"] == mock_cart_factory.return_value
        mock_cart_factory.assert_called_once_with(request)
