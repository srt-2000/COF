from __future__ import annotations

import pytest
from promo.promo import FreeProductPromo, TotalCartPromo
from promo.promo_factory import PromoFactory


class TestPromoFactory:
    @staticmethod
    def test_get_total_cart_promo(mocker, valid_promo):
        """Test getting TotalCartPromo for type=1"""
        valid_promo.promo_type = 1
        mocker.patch("promo.models.Promo.objects.get", return_value=valid_promo)

        result = PromoFactory.get_promo(valid_promo.id)
        assert isinstance(result, TotalCartPromo)
        assert result.promo == valid_promo

    @staticmethod
    def test_get_free_product_promo(mocker, valid_promo):
        """Test getting FreeProductPromo for type=2"""
        valid_promo.promo_type = 2
        mocker.patch("promo.models.Promo.objects.get", return_value=valid_promo)

        result = PromoFactory.get_promo(valid_promo.id)
        assert isinstance(result, FreeProductPromo)
        assert result.promo == valid_promo

    @staticmethod
    @pytest.mark.parametrize(
        "promo_type,expected_class",
        [
            (1, TotalCartPromo),
            (2, FreeProductPromo),
            (3, type(None)),
        ],
    )
    def test_promo_factory_return_types(mocker, valid_promo, promo_type, expected_class):
        """Parametrized test for all promo types"""
        valid_promo.promo_type = promo_type
        mocker.patch("promo.models.Promo.objects.get", return_value=valid_promo)

        result = PromoFactory.get_promo(valid_promo.id)
        assert isinstance(result, expected_class)
