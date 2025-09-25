"""Tests for cart storage.

This module contains tests for the SessionCartStorage class including:
- Tests for storage initialization and basic operations
- Integration tests for storage functionality
- Mock tests for storage operations
"""

from __future__ import annotations

import pytest
from cart.domains import CartData
from cart.storage import SessionCartStorage


class TestSessionCartStorage:
    """Tests for SessionCartStorage class."""

    def test_init(
        self,
        mock_session,
        mock_settings: None,
    ) -> None:
        """Test storage initialization.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
        """
        storage = SessionCartStorage(mock_session)

        assert storage.session == mock_session
        assert storage._key == "cart"

    def test_load_empty(
        self,
        mock_session,
        mock_settings: None,
    ) -> None:
        """Test loading empty cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
        """
        storage = SessionCartStorage(mock_session)
        result = storage.load()

        mock_session.get.assert_called_once_with("cart", {})
        assert result == {}

    def test_load_with_data(
        self,
        mock_session,
        mock_settings: None,
        sample_cart_data: dict[str, CartData],
    ) -> None:
        """Test loading cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
            sample_cart_data: Sample cart data to load
        """
        mock_session.get.return_value = sample_cart_data
        storage = SessionCartStorage(mock_session)
        result = storage.load()

        mock_session.get.assert_called_once_with("cart", {})
        assert result == sample_cart_data

    def test_save(
        self,
        mock_session,
        mock_settings: None,
        sample_cart_data: dict[str, CartData],
    ) -> None:
        """Test saving cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
            sample_cart_data: Sample cart data to save
        """
        storage = SessionCartStorage(mock_session)
        storage.save(sample_cart_data)

        mock_session.__setitem__.assert_called_once_with("cart", sample_cart_data)
        assert mock_session.modified is True

    def test_clear(
        self,
        mock_session,
        mock_settings: None,
        mocker,
    ) -> None:
        """Test clearing cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
        """
        mock_session.__contains__ = mocker.Mock(return_value=True)
        storage = SessionCartStorage(mock_session)
        storage.clear()

        mock_session.__delitem__.assert_called_once_with("cart")
        assert mock_session.modified is True


class TestSessionCartStorageIntegration:
    """Integration tests for SessionCartStorage."""

    def test_save_and_load(
        self,
        mock_session,
        mock_settings: None,
        sample_cart_data: dict[str, CartData],
    ) -> None:
        """Test saving and loading cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
            sample_cart_data: Sample cart data to test with
        """
        storage = SessionCartStorage(mock_session)

        storage.save(sample_cart_data)
        mock_session.__setitem__.assert_called_once_with("cart", sample_cart_data)

        mock_session.get.return_value = sample_cart_data
        result = storage.load()
        assert result == sample_cart_data

    def test_clear_and_load(
        self,
        mock_session,
        mock_settings: None,
        sample_cart_data: dict[str, CartData],
        mocker,
    ) -> None:
        """Test clearing and loading cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
            sample_cart_data: Sample cart data to test with
        """
        storage = SessionCartStorage(mock_session)

        storage.save(sample_cart_data)
        mock_session.__setitem__.assert_called_once_with("cart", sample_cart_data)

        mock_session.__contains__ = mocker.Mock(return_value=True)
        storage.clear()
        mock_session.__delitem__.assert_called_once_with("cart")

        mock_session.get.return_value = {}
        result = storage.load()
        assert result == {}


class TestSessionCartStorageMock:
    """Tests using mock objects."""

    @pytest.mark.parametrize(
        "cart_data",
        [
            {},  # Empty cart
            {"1": {"quantity": 1, "price": 100.00}},  # Single item
            {  # Multiple items
                "1": {"quantity": 2, "price": 100.00},
                "2": {"quantity": 1, "price": 200.00},
            },
        ],
    )
    def test_save_with_different_data(
        self,
        mock_session,
        mock_settings: None,
        cart_data: dict[str, CartData],
    ) -> None:
        """Test saving different cart data.

        Args:
            mock_session: Mocked session object
            mock_settings: Mocked settings
            cart_data: Cart data to test with
        """
        storage = SessionCartStorage(mock_session)
        storage.save(cart_data)

        mock_session.__setitem__.assert_called_once_with("cart", cart_data)
        assert mock_session.modified is True

    def test_load_with_mock_session(
        self,
        mock_settings: None,
        sample_cart_data: dict[str, CartData],
        mocker,
    ) -> None:
        """Test loading with mocked session.

        Args:
            mock_settings: Mocked settings
            sample_cart_data: Sample cart data to test with
            mocker: Pytest mocker fixture
        """
        mock_session = mocker.Mock()
        mock_session.get.return_value = sample_cart_data
        mock_session.__setitem__ = mocker.Mock()
        mock_session.__delitem__ = mocker.Mock()
        mock_session.__contains__ = mocker.Mock(return_value=True)
        mock_session.__getitem__ = mocker.Mock(return_value={})

        storage = SessionCartStorage(mock_session)
        result = storage.load()

        mock_session.get.assert_called_once_with("cart", {})
        assert result == sample_cart_data

    def test_clear_with_mock_session(
        self,
        mock_settings: None,
        mocker,
    ) -> None:
        """Test clearing with mocked session.

        Args:
            mock_settings: Mocked settings
            mocker: Pytest mocker fixture
        """
        mock_session = mocker.Mock()
        mock_session.__contains__ = mocker.Mock(return_value=True)
        mock_session.__setitem__ = mocker.Mock()
        mock_session.__delitem__ = mocker.Mock()
        mock_session.__getitem__ = mocker.Mock(return_value={})

        storage = SessionCartStorage(mock_session)
        storage.clear()

        mock_session.__delitem__.assert_called_once_with("cart")
        assert mock_session.modified is True
