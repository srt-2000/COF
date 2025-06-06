"""
Interface for a shopping cart.

Defines the required methods for any cart implementation, including
adding, removing, clearing items, iterating over cart contents,
getting the total price, and retrieving a specific item.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from decimal import Decimal
from typing import Optional, TypedDict

from catalog.models import Product


class CartItemTypedDict(TypedDict):
    product: object
    quantity: int
    price: Decimal
    total_price: Decimal


class CartDataTypedDict(TypedDict):
    quantity: int
    price: float | None


class CartItemServiceTypedDict(TypedDict):
    product: Product
    quantity: int
    price: Decimal
    total_price: Decimal


class ICart(ABC):
    """
    Abstract base class for a shopping cart.
    """

    @abstractmethod
    def add(self, product_id: int, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add a product to the cart or update its quantity.

        Args:
            product_id (int): The ID of the product to add.
            quantity (int, optional): The quantity to add. Defaults to 1.
            override_quantity (bool, optional): If True, set quantity instead of incrementing. Defaults to False.
        """
        pass

    @abstractmethod
    def remove(self, product_id: int) -> None:
        """
        Remove a product from the cart.

        Args:
            product_id (int): The ID of the product to remove.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all items from the cart.
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[CartItemTypedDict]:
        """
        Iterate over items in the cart.

        Returns:
            Iterator[CartItemTypedDict]: An iterator over cart items.
        """
        pass

    @abstractmethod
    def __len__(self) -> int:
        """
        Get the total number of items in the cart.

        Returns:
            int: The total quantity of all items.
        """
        pass

    @abstractmethod
    def get_total_price(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.

        Returns:
            Decimal: The total price.
        """
        pass

    @abstractmethod
    def get_item(self, product_id: int) -> CartItemTypedDict | None:
        """
        Retrieve a specific item from the cart.

        Args:
            product_id (int): The ID of the product.

        Returns:
            Optional[CartItemTypedDict]: The cart item if found, else None.
        """
        pass


class IStorage(ABC):
    """Abstract base class for cart storage implementations.

    This interface defines methods for persisting cart data between requests.
    Implementations can use different storage backends (session, database, etc).
    """

    @abstractmethod
    def load(self) -> dict[str, CartDataTypedDict]:
        """Load cart data from storage.

        Returns:
            dict[str, CartDataTypedDict]: Dictionary mapping product IDs to cart data.
        """
        pass

    @abstractmethod
    def save(self, cart_data: dict[str, CartDataTypedDict]) -> None:
        """Save cart data to storage.

        Args:
            cart_data (dict[str, CartDataTypedDict]): Dictionary mapping product IDs to cart data.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Remove all cart data from storage."""
        pass


class ICartProductService(ABC):
    """Abstract base class for cart product service implementations.

    This interface defines methods for retrieving product information
    and preparing cart items with proper pricing calculations.
    """

    @abstractmethod
    def get_products(self, product_ids: list[int]) -> dict[int, Product]:
        """Retrieve products by their IDs.

        Args:
            product_ids (list[int]): List of product IDs to retrieve.

        Returns:
            dict[int, Product]: Dictionary mapping product IDs to Product instances.
        """
        pass

    @abstractmethod
    def calculate_item_total(self, price: Decimal, quantity: int) -> Decimal:
        """Calculate total price for a cart item.

        Args:
            price (Decimal): Unit price of the product.
            quantity (int): Quantity of the product.

        Returns:
            Decimal: Total price (price * quantity).
        """
        pass

    @abstractmethod
    def prepare_item(self, product: Product, quantity: int) -> CartItemServiceTypedDict:
        """Prepare a cart item from a product.

        Args:
            product (Product): Product instance.
            quantity (int): Quantity of the product.

        Returns:
            CartItemServiceTypedDict: Dictionary containing product info and calculated prices.
        """
        pass
