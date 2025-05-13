from __future__ import annotations

from typing import TYPE_CHECKING

import django.test
import pytest
from catalog.models import Product, ProductCategory, ProductManufacture, ProductRegion, ProductSort, ProductType
from django.contrib.auth import get_user_model

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
def user_with_email(test_user: 'User') -> 'User':
    """Modifies test_user for email authentication tests."""
    test_user.email = "auth@example.com"
    test_user.set_password("secure123")
    test_user.save()
    return test_user

@pytest.fixture
def inactive_user(test_user: 'User') -> 'User':
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
