from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

import django.test
import pytest
from cart.cart import Cart
from cart.factory import CartFactory
from cart.product_service import CartProductService
from cart.storage import SessionCartStorage
from catalog.models import Product, ProductCategory, ProductManufacture, ProductRegion, ProductSort, ProductType
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.utils import timezone
from promo.models import Promo
from promo.promo import BasePromo

from coffeeshop.users.authentication import EmailAuthBackend

if TYPE_CHECKING:
    User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db: django.test.TestCase) -> None:
    """Enable database access for all tests.
    This fixture runs automatically for all tests.
    """
    pass


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


@pytest.fixture
def mock_storage(mocker) -> SessionCartStorage:
    """Create a mock storage for cart testing.

    Returns:
        SessionCartStorage: A mock storage instance
    """
    storage = mocker.Mock(spec=SessionCartStorage)
    storage.load.return_value = {}
    return storage


@pytest.fixture
def mock_product_service(sample_products, mocker) -> CartProductService:
    """Create a mock product service for cart testing.

    Returns:
        CartProductService: A mock product service instance
    """
    service = mocker.Mock(spec=CartProductService)
    service.get_products.side_effect = lambda ids: {i: sample_products[i] for i in ids if i in sample_products}
    service.prepare_item.side_effect = lambda product, quantity: {
        "product": product,
        "quantity": quantity,
        "price": product["price"],
        "total_price": product["price"] * quantity,
    }
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


@pytest.fixture
def mock_request(mocker) -> HttpRequest:
    """Create a mock request for testing.

    Returns:
        HttpRequest: A mock request object
    """
    request = mocker.Mock(spec=HttpRequest)
    request.session = {}
    return request


@pytest.fixture
def mock_cart_factory(mocker) -> None:
    """Patch CartFactory.create_from_session to return a mock cart."""
    mock = mocker.patch.object(CartFactory, "create_from_session")
    mock.return_value = mocker.Mock()
    return mock


@pytest.fixture
def mock_session(mocker):
    """Create a mock session for testing.

    Returns:
        Mock: A mock session instance
    """
    session = mocker.Mock()
    session.get.return_value = {}
    session.modified = False
    # Configure session to support item assignment like a dict
    session.__setitem__ = mocker.Mock()
    session.__delitem__ = mocker.Mock()
    session.__contains__ = mocker.Mock(return_value=True)
    # Make session behave like a dict for item access
    session.__getitem__ = mocker.Mock(return_value={})
    return session


@pytest.fixture
def mock_storage_class(mocker) -> None:
    """Patch SessionCartStorage to return a mock instance."""
    mock = mocker.patch("cart.factory.SessionCartStorage")
    mock.return_value = mocker.Mock(spec=SessionCartStorage)
    return mock


@pytest.fixture
def mock_product_service_class(mocker) -> None:
    """Patch CartProductService to return a mock instance."""
    mock = mocker.patch("cart.factory.CartProductService")
    mock.return_value = mocker.Mock(spec=CartProductService)
    return mock


@pytest.fixture
def mock_cart_class(mocker) -> None:
    """Patch Cart to return a mock instance."""
    mock = mocker.patch("cart.factory.Cart")
    mock.return_value = mocker.Mock(spec=Cart)
    return mock


@pytest.fixture
def mock_product(mocker):
    """Create a mock product for testing.

    Returns:
        Mock: A mock product instance
    """
    product = mocker.Mock(spec=Product)
    product.id = 1
    product.name = "Test Product"
    product.price = Decimal("100.00")
    return product


@pytest.fixture
def mock_product_queryset(mocker):
    """Create a mock product queryset for testing.

    Returns:
        Mock: A mock queryset instance
    """
    queryset = mocker.Mock()
    queryset.filter.return_value = queryset
    return queryset


@pytest.fixture
def mock_product_model(mocker) -> None:
    """Patch Product model for testing."""
    mock = mocker.patch("cart.product_service.Product")
    return mock


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
def order_item_data() -> dict[str, str | int | Decimal]:
    """Create sample order item data for testing.

    Returns:
        dict[str, str | int | Decimal]: Sample order item data with:
            - product_id: int
            - product_name: str
            - quantity: int
            - price: Decimal
    """
    return {"product_id": 1, "product_name": "Test Product", "quantity": 2, "price": Decimal("100.00")}


@pytest.fixture(autouse=True)
def patch_product_get(mocker):
    mock_get = mocker.patch("catalog.models.Product.objects.get")

    def fake_get(id):
        product = mocker.Mock()
        product.id = id
        product.price = Decimal("100.00") if id == 1 else Decimal("200.00")
        return product

    mock_get.side_effect = fake_get
    return mock_get


# test_promo fixtures


@pytest.fixture
def mock_promo_request():
    """Fixture for mocking HTTP request with session"""

    class MockRequest:
        def __init__(self):
            self.session = {}

    return MockRequest()


@pytest.fixture
def mock_promo_cart(mocker):
    """Fixture for mocking cart with default values using pytest-mock"""
    cart = mocker.Mock()
    cart.get_total_price.return_value = 800  # Discounted price
    cart.get_cart_total.return_value = 1000  # Regular price
    mocker.patch("cart.factory.CartFactory.create_from_session", return_value=cart)
    return cart


@pytest.fixture
def valid_promo(mocker):
    """Fixture for mocking active promo code"""
    promo = mocker.Mock()
    promo.name = "TEST10"
    mocker.patch("promo.models.Promo.objects.get", return_value=promo)
    return promo


@pytest.fixture
def invalid_promo(mocker):
    """Fixture for mocking non-existent promo code"""
    mocker.patch("promo.models.Promo.objects.get", side_effect=Promo.DoesNotExist)
    return None


@pytest.fixture
def active_promo():
    """Active Promo fixture"""
    from promo.models import Promo, PromoTypeEnum

    now = timezone.now()
    return Promo.objects.create(
        id=1,
        name="ACTIVE1",
        promo_type=PromoTypeEnum.TOTAL_CART.value,
        description="Test description",
        is_active=True,
        date_start=now - timedelta(days=10),
        date_end=now + timedelta(days=10),
        min_cart_total=Decimal("100.00"),
        discount=Decimal("10.00"),
    )


@pytest.fixture
def inactive_promo():
    """Inactive Promo fixture"""
    from promo.models import Promo, PromoTypeEnum

    now = timezone.now()
    return Promo.objects.create(
        id=2,
        name="INACTIVE1",
        promo_type=PromoTypeEnum.FREE_PRODUCT.value,
        description="Test description",
        is_active=False,
        date_start=now - timedelta(days=10),
        date_end=now - timedelta(days=5),
        min_cart_total=Decimal("50.00"),
        discount=Decimal("5.00"),
    )


# Удалить фикстуру promo_type полностью


@pytest.fixture
def promo_form_data(active_promo):
    """Valid form data"""
    return {"active_promos": active_promo.id}


@pytest.fixture
def base_promo_mock(mocker):
    """Fixture using pytest-mock"""
    # Create mock using pytest-mock
    mock_promo = mocker.Mock(
        spec=BasePromo,
        # Set return values for abstract methods
        apply_promo=Decimal("100"),
        valid_cart=True,
    )

    # For non-functional methods use original implementation
    mock_promo.is_valid_period = mocker.Mock(side_effect=BasePromo.is_valid_period)
    mock_promo.is_valid_id = mocker.Mock(side_effect=BasePromo.is_valid_id)
    mock_promo.valid_promo = mocker.Mock(side_effect=BasePromo.valid_promo)

    return mock_promo


# Добавляем новые фикстуры для order после существующих order фикстур
@pytest.fixture
def mock_cart_for_order(mocker):
    """Create a mock cart for order testing."""
    cart = mocker.Mock()
    # Configure the mock to support iteration
    cart_items = [
        {
            "product": mocker.Mock(id=1, name="Test Product", price=Decimal("100.00")),
            "quantity": 2,
            "price": Decimal("100.00"),
            "total_price": Decimal("200.00"),
        }
    ]
    cart.__iter__ = mocker.Mock(return_value=iter(cart_items))
    cart.get_total_price.return_value = Decimal("200.00")
    cart.clear = mocker.Mock()
    return cart


@pytest.fixture
def mock_form_data():
    """Create mock form data for order testing."""
    return {"delivery_address": "123 Main Street, Apt 4B", "phone": "+79001234567"}


@pytest.fixture
def mock_applied_promo_id():
    """Create mock applied promo ID for order testing."""
    return 1


@pytest.fixture
def mock_promo_context():
    """Create mock promo context for order testing."""
    return {"applied_promo_name": "TEST10", "applied_promo_status": True}


# Обновляем существующие фикстуры
@pytest.fixture
def mock_order_service(mocker):
    """Mock OrderService for testing with new signature."""
    from order.services import OrderService

    def mock_create_order(self, user, cart, form_data, applied_promo_id):
        """Mock implementation of create_order with new signature."""
        return {
            "order_id": 1,
            "user_email": user.email,
            "delivery_address": form_data["delivery_address"],
            "phone": form_data["phone"],
            "total_price": Decimal("200.00"),
            "time_created": "2024-03-20 12:00:00",
            "items": [{"product_id": 1, "product_name": "Test Product", "quantity": 2, "price": Decimal("100.00")}],
            "applied_promo_name": "TEST10",
            "applied_promo_status": True,
        }

    mocker.patch.object(OrderService, "create_order", mock_create_order)


@pytest.fixture
def mock_order_notification(mocker):
    """Mock OrderNotification for testing with new signature."""
    from order.services import EmailOrderNotification

    def mock_send_notification(self, order_id):
        """Mock implementation with new signature."""
        pass

    mocker.patch.object(EmailOrderNotification, "send_order_notification", mock_send_notification)


@pytest.fixture
def mock_order_repository(mocker):
    """Mock OrderRepository for testing with new signature."""
    from order.services import DatabaseOrderRepository

    def mock_save_order(self, order_data):
        """Mock implementation of save_order with new signature."""
        # Add order_id if not present
        if "order_id" not in order_data:
            order_data = order_data.copy()
            order_data["order_id"] = 1
        # Add time_created if not present
        if "time_created" not in order_data:
            order_data = order_data.copy()
            order_data["time_created"] = "2024-03-20 12:00:00"
        return order_data

    mocker.patch.object(DatabaseOrderRepository, "save_order", mock_save_order)


@pytest.fixture
def mock_render(mocker):
    """Mock render function for cart view testing."""
    return mocker.patch("cart.views.render")


@pytest.fixture
def mock_get_object_or_404(mocker):
    """Mock get_object_or_404 function for cart view testing."""
    return mocker.patch("cart.views.get_object_or_404")


@pytest.fixture
def mock_redirect(mocker):
    """Mock redirect function for cart view testing."""
    return mocker.patch("cart.views.redirect")
