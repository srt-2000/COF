from __future__ import annotations

import pytest
from promo.context_processor import promo_status


@pytest.mark.usefixtures("mock_promo_cart")
class TestPromoContextProcessor:
    """Unit tests for context_processor."""

    @staticmethod
    def test_promo_status_no_request(mock_promo_request) -> None:
        result = promo_status(mock_promo_request)
        assert result == {
            "applied_promo_name": None,
            "applied_promo_status": False,
        }

    @staticmethod
    def test_valid_promo(mock_promo_request, valid_promo):
        """Test scenario with valid applied promo code"""
        mock_promo_request.session["applied_promo_id"] = 1
        result = promo_status(mock_promo_request)

        assert result["applied_promo_name"] == "TEST10"
        assert result["applied_promo_status"] is True

    @staticmethod
    def test_invalid_promo(mock_promo_request, invalid_promo):
        """Test scenario with non-existent promo code"""
        mock_promo_request.session["applied_promo_id"] = 999
        result = promo_status(mock_promo_request)

        assert result["applied_promo_name"] is None
        assert result["applied_promo_status"] is False

    @staticmethod
    def test_inactive_promo_discount(mock_promo_request, mock_promo_cart, valid_promo):
        """Test scenario when promo exists but discount isn't applied"""
        mock_promo_request.session["applied_promo_id"] = 1
        mock_promo_cart.get_total_price.return_value = 1000  # No discount applied

        result = promo_status(mock_promo_request)
        assert result["applied_promo_name"] == "TEST10"
        assert result["applied_promo_status"] is False
