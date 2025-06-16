from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import django.test
import pytest
from cart.cart import Cart
from cart.context_processor import CartContext
from cart.factory import CartFactory
from cart.interfaces import CartItemTypedDict, ICart
from cart.product_service import CartProductService
from cart.storage import SessionCartStorage
from catalog.models import Product, ProductCategory, ProductManufacture, ProductRegion, ProductSort, ProductType
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from coffeeshop.users.authentication import EmailAuthBackend

if TYPE_CHECKING:
    User = get_user_model()


@pytest.fixture
def category_object_tea() -> ProductCategory:
    """Create a tea category fixture.

    Returns:
        ProductCategory: A tea category instance with name 'TEA' and slug 'tea'
    """
    return ProductCategory.objects.create(name="TEA", slug="tea")


@pytest.fixture
def category_object_coffee() -> ProductCategory:
    """Create a coffee category fixture.

    Returns:
        ProductCategory: A coffee category instance with name 'COFFEE' and slug 'coffee'
    """
    return ProductCategory.objects.create(name="COFFEE", slug="coffee")


@pytest.fixture
def category_object_accessories() -> ProductCategory:
    """Create an accessories category fixture.

    Returns:
        ProductCategory: An accessories category instance with name 'ACCESSORIES' and slug 'accessories'
    """
    return ProductCategory.objects.create(name="ACCESSORIES", slug="accessories")


@pytest.fixture
def category_null_name_object() -> ProductCategory:
    """Create a category fixture with empty name for validation testing.

    Returns:
        ProductCategory: A category instance with empty name
    """
    return ProductCategory(name="")


@pytest.fixture
def category_long_name_object() -> ProductCategory:
    """Create a category fixture with name exceeding max length for validation testing.

    Returns:
        ProductCategory: A category instance with name length > 100 characters
    """
    return ProductCategory(name="a" * 101)


@pytest.fixture
def category_duplicate_slug_object(category_object_tea: ProductCategory) -> ProductCategory:
    """Create a category fixture with duplicate slug for validation testing.

    Args:
        category_object_tea: Existing tea category fixture

    Returns:
        ProductCategory: A category instance with duplicate slug
    """
    return ProductCategory(name="Different Tea", slug="tea")


@pytest.fixture
def sort_object() -> ProductSort:
    """Create a product sort fixture.

    Returns:
        ProductSort: A sort instance with name 'Arabica' and slug 'arabica'
    """
    return ProductSort.objects.create(name="Arabica", slug="arabica")


@pytest.fixture
def type_object() -> ProductType:
    """Create a product type fixture.

    Returns:
        ProductType: A type instance with name 'Green' and slug 'green'
    """
    return ProductType.objects.create(name="Green", slug="green")


@pytest.fixture
def region_object() -> ProductRegion:
    """Create a product region fixture.

    Returns:
        ProductRegion: A region instance with name 'Ethiopia' and slug 'ethiopia'
    """
    return ProductRegion.objects.create(name="Ethiopia", slug="ethiopia")


@pytest.fixture
def manufacture_object() -> ProductManufacture:
    """Create a product manufacture fixture.

    Returns:
        ProductManufacture: A manufacture instance with name 'Lavazza' and slug 'lavazza'
    """
    return ProductManufacture.objects.create(name="Lavazza", slug="lavazza")


@pytest.fixture
def product_object_tea(category_object_tea: ProductCategory) -> Product:
    """Create a tea product fixture.

    Args:
        category_object_tea: Tea category fixture

    Returns:
        Product: A tea product instance
    """
    return Product.objects.create(
        name="test_product_1",
        slug="test-product-1",
        description="some description some description some description",
        price="1000",
        category=category_object_tea,
    )


@pytest.fixture
def product_object_coffee(category_object_coffee: ProductCategory) -> Product:
    """Create a coffee product fixture.

    Args:
        category_object_coffee: Coffee category fixture

    Returns:
        Product: A coffee product instance
    """
    return Product.objects.create(
        name="test_product_2",
        slug="test-product-2",
        description="coffee description",
        price="2000",
        category=category_object_coffee,
    )


@pytest.fixture
def product_object_accessories(category_object_accessories: ProductCategory) -> Product:
    """Create an accessories product fixture.

    Args:
        category_object_accessories: Accessories category fixture

    Returns:
        Product: An accessories product instance
    """
    return Product.objects.create(
        name="test_product_3",
        slug="test-product-3",
        description="accessories description",
        price="3000",
        category=category_object_accessories,
    )


@pytest.fixture
def product_null_name_object(category_object_tea: ProductCategory) -> Product:
    """Create a product fixture with empty name for validation testing.

    Args:
        category_object_tea: Tea category fixture

    Returns:
        Product: A product instance with empty name
    """
    return Product(
        name="", slug="test-product-2", description="description", price="1000", category=category_object_tea
    )


@pytest.fixture
def product_long_name_object(category_object_tea: ProductCategory) -> Product:
    """Create a product fixture with name exceeding max length for validation testing.

    Args:
        category_object_tea: Tea category fixture

    Returns:
        Product: A product instance with name length > 250 characters
    """
    return Product(
        name="a" * 251, slug="test-product-3", description="description", price="1000", category=category_object_tea
    )


@pytest.fixture
def product_duplicate_slug_object(category_object_tea: ProductCategory, product_object_tea: Product) -> Product:
    """Create a product fixture with duplicate slug for validation testing.

    Args:
        category_object_tea: Tea category fixture
        product_object_tea: Existing tea product fixture

    Returns:
        Product: A product instance with duplicate slug
    """
    return Product(
        name="test_product_4",
        slug="test-product-1",
        description="description",
        price="1000",
        category=category_object_tea,
    )


@pytest.fixture
def product_with_all_relations(
    category_object_tea: ProductCategory,
    sort_object: ProductSort,
    type_object: ProductType,
    region_object: ProductRegion,
    manufacture_object: ProductManufacture,
) -> Product:
    """Create a product fixture with all possible relations.

    Args:
        category_object_tea: Tea category fixture
        sort_object: Product sort fixture
        type_object: Product type fixture
        region_object: Product region fixture
        manufacture_object: Product manufacture fixture

    Returns:
        Product: A product instance with all relations set
    """
    return Product.objects.create(
        name="full_product",
        slug="full-product",
        description="full description",
        price="2000",
        category=category_object_tea,
        sort=sort_object,
        product_type=type_object,
        region=region_object,
        manufacture=manufacture_object,
    )


@pytest.fixture
def multiple_products(
    category_object_tea: ProductCategory,
    category_object_coffee: ProductCategory,
    category_object_accessories: ProductCategory,
) -> list[Product]:
    """Create multiple product fixtures for pagination testing.
    Creates 3 products for each category (tea, coffee, accessories).

    Args:
        category_object_tea: Tea category fixture
        category_object_coffee: Coffee category fixture
        category_object_accessories: Accessories category fixture

    Returns:
        List[Product]: List of 9 product instances (3 for each category)
    """
    products = []

    for i in range(3):
        products.append(
            Product.objects.create(
                name=f"tea_product_{i}",
                slug=f"tea-product-{i}",
                description=f"tea description {i}",
                price=f"{1000 + i * 100}",
                category=category_object_tea,
            )
        )
        products.append(
            Product.objects.create(
                name=f"coffee_product_{i}",
                slug=f"coffee-product-{i}",
                description=f"coffee description {i}",
                price=f"{2000 + i * 100}",
                category=category_object_coffee,
            )
        )
        products.append(
            Product.objects.create(
                name=f"accessories_product_{i}",
                slug=f"accessories-product-{i}",
                description=f"accessories description {i}",
                price=f"{3000 + i * 100}",
                category=category_object_accessories,
            )
        )
    return products


@pytest.fixture
def user_data() -> dict[str, str]:
    """Create a fixture with valid user data for testing forms.

    Returns:
        dict[str, str]: Dictionary containing valid user data for registration and login forms.
        Keys: username, email, first_name, last_name, password1, password2
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password1": "testpass123",
        "password2": "testpass123",
    }


@pytest.fixture
def test_user() -> User:
    """Create a test user in the database for testing.

    Returns:
        User: A test user instance with predefined data:
            - username: 'existinguser'
            - email: 'existing@example.com'
            - password: 'existing123'
            - first_name: 'Existing'
            - last_name: 'User'
    """
    User = get_user_model()
    return User.objects.create_user(
        username="existinguser",
        email="existing@example.com",
        password="existing123",
        first_name="Existing",
        last_name="User",
    )


@pytest.fixture
def backend() -> EmailAuthBackend:
    """Fixture providing an instance of EmailAuthBackend."""
    return EmailAuthBackend()


@pytest.fixture
def user_with_email(test_user: User) -> User:
    """Modifies test_user for email authentication tests."""
    test_user.email = "auth@example.com"
    test_user.set_password("secure123")
    test_user.save()
    return test_user


@pytest.fixture
def inactive_user(test_user: User) -> User:
    """Creates an inactive user for testing."""
    test_user.email = "inactive@example.com"
    test_user.set_password("inactive123")
    test_user.is_active = False
    test_user.save()
    return test_user


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: django.test.TestCase) -> None:
    """Enable database access for all tests.
    This fixture runs automatically for all tests.
    """
    pass


@pytest.fixture
def mock_storage() -> SessionCartStorage:
    """Create a mock storage for cart testing.

    Returns:
        SessionCartStorage: A mock storage instance
    """
    storage = MagicMock(spec=SessionCartStorage)
    storage.load.return_value = {}
    return storage


@pytest.fixture
def mock_product_service() -> CartProductService:
    """Create a mock product service for cart testing.

    Returns:
        CartProductService: A mock product service instance
    """
    service = MagicMock(spec=CartProductService)
    service.get_products.return_value = {}
    service.prepare_item.return_value = {"id": 1, "name": "Test Product", "price": Decimal("100.00"), "quantity": 1}
    return service


@pytest.fixture
def cart(mock_storage: SessionCartStorage, mock_product_service: CartProductService) -> Cart:
    """Create a cart instance for testing.

    Args:
        mock_storage: Mock storage fixture
        mock_product_service: Mock product service fixture

    Returns:
        Cart: A cart instance with mock dependencies
    """
    return Cart(storage=mock_storage, product_service=mock_product_service)


@pytest.fixture
def sample_products() -> dict[int, dict]:
    """Create sample products for testing.

    Returns:
        dict: A dictionary of sample products
    """
    return {
        1: {"id": 1, "name": "Product 1", "price": Decimal("100.00")},
        2: {"id": 2, "name": "Product 2", "price": Decimal("200.00")},
    }


class MockCart(ICart):
    """Mock implementation of ICart for testing."""

    def __init__(self) -> None:
        self._items: dict[int, CartItemTypedDict] = {}

    def add(self, product_id: int, quantity: int = 1, override_quantity: bool = False) -> None:
        if product_id not in self._items:
            self._items[product_id] = {
                "product": {"id": product_id, "name": f"Product {product_id}", "price": Decimal("100.00")},
                "quantity": 0,
                "price": Decimal("100.00"),
                "total_price": Decimal("0.00"),
            }

        if override_quantity:
            self._items[product_id]["quantity"] = quantity
        else:
            self._items[product_id]["quantity"] += quantity

        self._items[product_id]["total_price"] = self._items[product_id]["price"] * self._items[product_id]["quantity"]

    def remove(self, product_id: int) -> None:
        if product_id in self._items:
            del self._items[product_id]

    def clear(self) -> None:
        self._items.clear()

    def __iter__(self) -> Iterator[CartItemTypedDict]:
        return iter(self._items.values())

    def __len__(self) -> int:
        return sum(item["quantity"] for item in self._items.values())

    def get_total_price(self) -> Decimal:
        return sum(item["total_price"] for item in self._items.values())

    def get_item(self, product_id: int) -> CartItemTypedDict | None:
        return self._items.get(product_id)


@pytest.fixture
def mock_cart() -> MockCart:
    """Create a mock cart implementation for testing interfaces.

    Returns:
        MockCart: A mock implementation of ICart
    """
    return MockCart()


@pytest.fixture
def sample_cart_item() -> CartItemTypedDict:
    """Create a sample cart item for testing.

    Returns:
        CartItemTypedDict: A sample cart item
    """
    return {
        "product": {"id": 1, "name": "Test Product", "price": Decimal("100.00")},
        "quantity": 2,
        "price": Decimal("100.00"),
        "total_price": Decimal("200.00"),
    }


@pytest.fixture
def mock_request() -> HttpRequest:
    """Create a mock request for testing.

    Returns:
        HttpRequest: A mock request object
    """
    request = MagicMock(spec=HttpRequest)
    request.session = {}
    return request


@pytest.fixture
def mock_cart_factory() -> None:
    """Patch CartFactory.create_from_request to return a mock cart."""
    with patch.object(CartFactory, "create_from_request") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock session for testing.

    Returns:
        MagicMock: A mock session instance
    """
    session = MagicMock()
    session.get.return_value = {}
    session.modified = False
    return session


@pytest.fixture
def mock_storage_class() -> None:
    """Patch SessionCartStorage to return a mock instance."""
    with patch("cart.factory.SessionCartStorage") as mock:
        mock.return_value = MagicMock(spec=SessionCartStorage)
        yield mock


@pytest.fixture
def mock_product_service_class() -> None:
    """Patch CartProductService to return a mock instance."""
    with patch("cart.factory.CartProductService") as mock:
        mock.return_value = MagicMock(spec=CartProductService)
        yield mock


@pytest.fixture
def mock_cart_class() -> None:
    """Patch Cart to return a mock instance."""
    with patch("cart.factory.Cart") as mock:
        mock.return_value = MagicMock(spec=Cart)
        yield mock


@pytest.fixture
def mock_product() -> MagicMock:
    """Create a mock product for testing.

    Returns:
        MagicMock: A mock product instance
    """
    product = MagicMock(spec=Product)
    product.id = 1
    product.name = "Test Product"
    product.price = Decimal("100.00")
    return product


@pytest.fixture
def mock_product_queryset() -> MagicMock:
    """Create a mock product queryset for testing.

    Returns:
        MagicMock: A mock queryset instance
    """
    queryset = MagicMock()
    queryset.filter.return_value = queryset
    return queryset


@pytest.fixture
def mock_product_model() -> None:
    """Patch Product model for testing."""
    with patch("cart.product_service.Product") as mock:
        yield mock


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch Django settings for testing."""
    monkeypatch.setattr("cart.storage.settings.CART_SESSION_ID", "cart")


@pytest.fixture
def sample_cart_data() -> dict[str, dict]:
    """Create sample cart data for testing.

    Returns:
        dict: A dictionary of sample cart data
    """
    return {
        "1": {"quantity": 2, "price": 100.00},
        "2": {"quantity": 1, "price": 200.00},
    }


@pytest.fixture
def mock_cart_detail_view() -> None:
    """Patch CartDetailView for testing."""
    with patch("cart.views.CartDetailView") as mock:
        yield mock


@pytest.fixture
def mock_cart_add_view() -> None:
    """Patch CartAddView for testing."""
    with patch("cart.views.CartAddView") as mock:
        yield mock


@pytest.fixture
def mock_cart_update_view() -> None:
    """Patch CartUpdateView for testing."""
    with patch("cart.views.CartUpdateView") as mock:
        yield mock


@pytest.fixture
def mock_cart_remove_view() -> None:
    """Patch CartRemoveView for testing."""
    with patch("cart.views.CartRemoveView") as mock:
        yield mock


@pytest.fixture
def mock_cart_clear_view() -> None:
    """Patch CartClearView for testing."""
    with patch("cart.views.CartClearView") as mock:
        yield mock


@pytest.fixture
def mock_render() -> None:
    """Patch render function for testing."""
    with patch("cart.views.render") as mock:
        yield mock


@pytest.fixture
def mock_redirect() -> None:
    """Patch redirect function for testing."""
    with patch("cart.views.redirect") as mock:
        yield mock


@pytest.fixture
def mock_get_object_or_404() -> None:
    """Patch get_object_or_404 function for testing."""
    with patch("cart.views.get_object_or_404") as mock:
        yield mock


@pytest.fixture
def order_form_data() -> dict[str, str]:
    """Create sample order form data
    
    Returns:
        dict: Sample order form data with valid values
    """
    return {
        'phone': '+79001234567',
        'delivery_address': '123 Main Street, Apt 4B, City, 123456'
    }


@pytest.fixture
def invalid_order_form_data() -> dict[str, str]:
    """Create invalid order form data
    
    Returns:
        dict: Sample order form data with invalid values
    """
    return {
        'phone': '123',  # Invalid phone format
        'delivery_address': 'Short'  # Too short address
    }


@pytest.fixture
def mock_order_form(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock OrderCreateForm for testing
    
    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    from order.forms import OrderCreateForm
    
    def mock_clean(self):
        return self.cleaned_data
    
    monkeypatch.setattr(OrderCreateForm, 'clean', mock_clean)


@pytest.fixture
def order_item_data() -> dict[str, str | int | Decimal]:
    """Create sample order item data for testing.
    
    Returns:
        dict[str, str | int | Decimal]: Sample order item data with:
            - product_id: int
            - product_name: str
            - quantity: int
            - price: Decimal
    """
    return {
        'product_id': 1,
        'product_name': 'Test Product',
        'quantity': 2,
        'price': Decimal('100.00')
    }


@pytest.fixture
def order_data(test_user: User, order_item_data: dict[str, str | int | Decimal]) -> dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]:
    """Create sample order data for testing.
    
    Args:
        test_user: Test user fixture
        order_item_data: Order item data fixture
        
    Returns:
        dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]: Sample order data with:
            - order_id: int
            - user_email: str
            - delivery_address: str
            - phone: str
            - total_price: Decimal
            - time_created: str
            - items: list[dict[str, str | int | Decimal]]
    """
    return {
        'order_id': 1,
        'user_email': test_user.email,
        'delivery_address': '123 Main Street',
        'phone': '+79001234567',
        'total_price': Decimal('200.00'),
        'time_created': '2024-03-20 12:00:00',
        'items': [order_item_data]
    }


@pytest.fixture
def mock_order_service(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock OrderService for testing.
    
    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    from order.services import OrderService
    
    def mock_create_order(self, user: User, items: list[dict[str, str | int | Decimal]], total_price: Decimal, delivery_address: str, phone: str) -> dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]:
        """Mock implementation of create_order.
        
        Args:
            user: User creating the order
            items: List of items in the order
            total_price: Total price of the order
            delivery_address: Delivery address
            phone: Customer phone number
            
        Returns:
            dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]: Mock order data
        """
        return {
            'order_id': 1,
            'user_email': user.email,
            'delivery_address': delivery_address,
            'phone': phone,
            'total_price': total_price,
            'time_created': '2024-03-20 12:00:00',
            'items': items
        }
    
    monkeypatch.setattr(OrderService, 'create_order', mock_create_order)


@pytest.fixture
def mock_order_notification(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock OrderNotification for testing
    
    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    from order.services import EmailOrderNotification
    
    def mock_send_notification(self, order):
        pass
    
    monkeypatch.setattr(EmailOrderNotification, 'send_order_notification', mock_send_notification)


@pytest.fixture
def mock_order_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock OrderRepository for testing.
    
    Args:
        monkeypatch: pytest monkeypatch fixture
    """
    from order.services import DatabaseOrderRepository
    
    def mock_save_order(self, order_data: dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]) -> dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]:
        """Mock implementation of save_order.
        
        Args:
            order_data: Order data to save
            
        Returns:
            dict[str, str | int | Decimal | list[dict[str, str | int | Decimal]]]: Saved order data
        """
        # Add order_id if not present
        if 'order_id' not in order_data:
            order_data = order_data.copy()
            order_data['order_id'] = 1
        # Add time_created if not present
        if 'time_created' not in order_data:
            order_data = order_data.copy()
            order_data['time_created'] = '2024-03-20 12:00:00'
        return order_data
    
    monkeypatch.setattr(DatabaseOrderRepository, 'save_order', mock_save_order)
