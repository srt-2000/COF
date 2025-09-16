from __future__ import annotations

import pytest
from promo.promo import BasePromo, TotalCartPromo


class TestBasePromo:
    @staticmethod
    def test_is_valid_period_returns_true_for_active_promo(active_promo):
        base_promo_object = BasePromo(active_promo)
        assert base_promo_object.is_valid_period() is True

    @staticmethod
    def test_is_valid_period_returns_false_for_inactive_promo(inactive_promo):
        base_promo_object = BasePromo(inactive_promo)
        assert base_promo_object.is_valid_period() is False

    @staticmethod
    def test_is_valid_id_returns_true_for_matching_id(active_promo):
        base_promo_object = BasePromo(active_promo)
        assert base_promo_object.is_valid_id(active_promo.id) is True

    @staticmethod
    def test_is_valid_id_returns_false_for_different_id(active_promo):
        base_promo_object = BasePromo(active_promo)
        assert base_promo_object.is_valid_id(999) is False

    @staticmethod
    def test_valid_promo_returns_true_when_all_conditions_met(active_promo):
        base_promo_object = BasePromo(active_promo)
        assert base_promo_object.valid_promo(active_promo.id) is True

    @staticmethod
    def test_valid_promo_returns_false_for_wrong_id(active_promo):
        base_promo_object = BasePromo(active_promo)
        assert base_promo_object.valid_promo(999) is False

    @staticmethod
    def test_valid_promo_returns_false_for_inactive_promo(inactive_promo):
        base_promo_object = BasePromo(inactive_promo)
        assert base_promo_object.valid_promo(inactive_promo.id) is False


class TestTotalCartPromo:
    pass

    # @staticmethod
    # def test_valid_cart(mock_promo_cart, base_promo_mock):
    #     total_cart_promo_object = TotalCartPromo(base_promo_mock)
    #     total_cart_promo_object.min_cart_total = 800
    #     assert total_cart_promo_object.valid_cart(mock_promo_cart) is True
