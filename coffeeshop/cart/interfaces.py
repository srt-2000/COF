"""
Interfaces for the shopping cart and related services.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator
from decimal import Decimal
from typing import Optional

from cart.domains import CartData, CartItemServiceData
from catalog.models import Product


class ICart(ABC):
    """
    Abstract base class for a shopping cart implementation.
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
    def __iter__(self) -> Generator[CartItemServiceData, None, None]:
        """
        Iterate over items in the cart.
        Returns:
            Generator[CartItemServiceData, None, None]: An iterator over cart items.
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
    def get_cart_total(self) -> Decimal:
        """
        Get the total price of all items in the cart (without PROMO).
        Returns:
            Decimal: The total price.
        """
        pass

    @abstractmethod
    def get_total_price(self, promo_id: int | None = None) -> Decimal:
        """
        Calculate the total price of all items in the cart with applying PROMO.
        Returns:
            Decimal: The total price.
        """
        pass

    @abstractmethod
    def get_discount_sum(self, promo_id: int | None = None) -> Decimal:
        """
        Calculate the discount sum.
        Returns:
            Decimal: The discount sum.
        """
        pass

    @abstractmethod
    def get_item(self, product_id: int) -> CartItemServiceData | None:
        """
        Retrieve a specific item from the cart.
        Args:
            product_id (int): The ID of the product.
        Returns:
            Optional[CartItemServiceData]: The cart item if found, else None.
        """
        pass


class IStorage(ABC):
    """
    Abstract base class for cart storage implementations.
    """

    @abstractmethod
    def load(self) -> dict[str, CartData]:
        """
        Load cart data from storage.
        Returns:
            dict[str, CartData]: Dictionary mapping product IDs to cart data.
        """
        pass

    @abstractmethod
    def save(self, cart_data: dict[str, CartData]) -> None:
        """
        Save cart data to storage.
        Args:
            cart_data (dict[str, CartData]): Dictionary mapping product IDs to cart data.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all cart data from storage.
        """
        pass


class ICartProductService(ABC):
    """
    Abstract base class for cart product service implementations.
    """

    @abstractmethod
    def get_products(self, product_ids: list[int]) -> dict[int, Product]:
        """
        Retrieve products by their IDs.
        Args:
            product_ids (list[int]): List of product IDs to retrieve.
        Returns:
            dict[int, Product]: Dictionary mapping product IDs to Product instances.
        """
        pass

    @abstractmethod
    def calculate_item_total(self, price: float, quantity: int) -> float:
        """
        Calculate total price for a cart item.
        Args:
            price (float): Unit price of the product.
            quantity (int): Quantity of the product.
        Returns:
            float: Total price (price * quantity).
        """
        pass

    @abstractmethod
    def prepare_item(self, product: Product, quantity: int) -> CartItemServiceData:
        """
        Prepare a cart item from a product.
        Args:
            product (Product): Product instance.
            quantity (int): Quantity of the product.
        Returns:
            CartItemServiceData: Dictionary containing product info and calculated prices.
        """
        pass
