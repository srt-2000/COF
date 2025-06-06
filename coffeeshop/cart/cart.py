"""
Implementation of the ICart interface for a shopping cart.

This class provides functionality to add, remove, clear items, iterate over cart contents,
calculate the total price, and retrieve specific items.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from typing import Optional, TypedDict

from cart.interfaces import CartItemTypedDict, ICart, ICartProductService, IStorage


class Cart(ICart):
    """
    A shopping cart implementation that stores items in a session-based storage.
    """

    def __init__(self, storage: IStorage, product_service: ICartProductService) -> None:
        """
        Initialize the cart with storage and product service.

        Args:
            storage (IStorage): The storage interface for the cart.
            product_service (ICartProductService): The service interface for product operations.
        """
        self._storage = storage
        self._product_service = product_service
        self._cart = self._storage.load()

    def add(self, product_id: int, quantity: int = 1, override_quantity: bool = False) -> None:
        """
        Add a product to the cart or update its quantity.

        Args:
            product_id (int): The ID of the product to add.
            quantity (int, optional): The quantity to add. Defaults to 1.
            override_quantity (bool, optional): If True, set quantity instead of incrementing. Defaults to False.
        """
        product_id_str = str(product_id)
        if product_id_str not in self._cart:
            self._cart[product_id_str] = {"quantity": 0, "price": None}

        if override_quantity:
            self._cart[product_id_str]["quantity"] = quantity
        else:
            self._cart[product_id_str]["quantity"] += quantity

        self._storage.save(self._cart)

    def remove(self, product_id: int) -> None:
        """
        Remove a product from the cart.

        Args:
            product_id (int): The ID of the product to remove.

        Raises:
            ValueError: If the product is not found in the cart.
        """
        product_id_str = str(product_id)
        try:
            del self._cart[product_id_str]
            self._storage.save(self._cart)
        except KeyError:
            raise ValueError(f"Product with ID {product_id} not found") from None

    def clear(self) -> None:
        """
        Remove all items from the cart.
        """
        self._storage.clear()
        self._cart = {}

    def __iter__(self) -> Iterator[CartItemTypedDict]:
        """
        Iterate over items in the cart.

        Returns:
            Iterator[CartItemTypedDict]: An iterator over cart items.
        """
        product_ids = [int(id) for id in self._cart.keys()]
        products = self._product_service.get_products(product_ids)

        for product_id_str, item in self._cart.items():
            product_id = int(product_id_str)
            if product_id in products:
                product = products[product_id]
                if item["price"] is None:
                    item["price"] = product.price
                yield self._product_service.prepare_item(product, item["quantity"])

    def __len__(self) -> int:
        """
        Get the total number of items in the cart.

        Returns:
            int: The total quantity of all items.
        """
        return sum(item["quantity"] for item in self._cart.values())

    def get_total_price(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.

        Returns:
            Decimal: The total price.
        """
        total = sum(
            Decimal(item["price"]) * item["quantity"] for item in self._cart.values() if item["price"] is not None
        )
        return Decimal(total)

    def get_item(self, product_id: int) -> CartItemTypedDict | None:
        """
        Retrieve a specific item from the cart.

        Args:
            product_id (int): The ID of the product.

        Returns:
            Optional[CartItemTypedDict]: The cart item if found, else None.
        """
        product_id_str = str(product_id)
        if product_id_str not in self._cart:
            return None

        products = self._product_service.get_products([product_id])
        if product_id not in products:
            return None

        product = products[product_id]
        quantity = self._cart[product_id_str]["quantity"]
        return self._product_service.prepare_item(product, quantity)
