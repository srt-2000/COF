import pytest
from catalog.models import Product, Category, Sort, Type, Region, Manufacture
from django.urls import reverse


@pytest.fixture
def category_object_tea():
    return Category.objects.create(name="TEA", slug='tea')


@pytest.fixture
def category_object_coffee():
    return Category.objects.create(name="COFFEE", slug='coffee')


@pytest.fixture
def category_object_accessories():
    return Category.objects.create(name="ACCESSORIES", slug='accessories')


@pytest.fixture
def category_null_name_object():
    return Category(name="")  # null name


@pytest.fixture
def category_long_name_object():
    return Category(name="a" * 101)  # name max_length>100


@pytest.fixture
def category_duplicate_slug_object(category_object_tea):
    return Category(name="Different Tea", slug='tea')  # double slug


@pytest.fixture
def sort_object():
    return Sort.objects.create(name="Arabica", slug='arabica')


@pytest.fixture
def type_object():
    return Type.objects.create(name="Green", slug='green')


@pytest.fixture
def region_object():
    return Region.objects.create(name="Ethiopia", slug='ethiopia')


@pytest.fixture
def manufacture_object():
    return Manufacture.objects.create(name="Lavazza", slug='lavazza')


@pytest.fixture
def product_object_tea(category_object_tea):
    return Product.objects.create(name='test_product_1', slug='test-product-1',
                                  description='some description some description some description',
                                  price='1000', category=category_object_tea
                                  )


@pytest.fixture
def product_object_coffee(category_object_coffee):
    return Product.objects.create(name='test_product_2', slug='test-product-2',
                                  description='coffee description',
                                  price='2000', category=category_object_coffee
                                  )


@pytest.fixture
def product_object_accessories(category_object_accessories):
    return Product.objects.create(name='test_product_3', slug='test-product-3',
                                  description='accessories description',
                                  price='3000', category=category_object_accessories
                                  )


@pytest.fixture
def product_null_name_object(category_object_tea):
    return Product(name="",  # null name
                   slug='test-product-2', description='description',
                   price='1000', category=category_object_tea)


@pytest.fixture
def product_long_name_object(category_object_tea):
    return Product(name="a" * 251,  # name max_length>250
                   slug='test-product-3',
                   description='description',
                   price='1000',
                   category=category_object_tea)


@pytest.fixture
def product_duplicate_slug_object(category_object_tea, product_object_tea):
    return Product(name='test_product_4',
                   slug='test-product-1',  # double slug
                   description='description',
                   price='1000',
                   category=category_object_tea)


@pytest.fixture
def product_with_all_relations(category_object_tea, sort_object, type_object, region_object, manufacture_object):
    return Product.objects.create(name='full_product',
                                  slug='full-product',
                                  description='full description',
                                  price='2000',
                                  category=category_object_tea,
                                  sort=sort_object,
                                  type=type_object,
                                  region=region_object,
                                  manufacture=manufacture_object)


# for pagination testing
# Create 3 product objects for every Category = in total 9 objects
# And we have 3 pages for our tests
@pytest.fixture
def multiple_products(category_object_tea, category_object_coffee, category_object_accessories):
    products = []

    for i in range(3):
        products.append(Product.objects.create(
            name=f'tea_product_{i}',
            slug=f'tea-product-{i}',
            description=f'tea description {i}',
            price=f'{1000 + i * 100}',
            category=category_object_tea
        ))
        products.append(Product.objects.create(
            name=f'coffee_product_{i}',
            slug=f'coffee-product-{i}',
            description=f'coffee description {i}',
            price=f'{2000 + i * 100}',
            category=category_object_coffee
        ))
        products.append(Product.objects.create(
            name=f'accessories_product_{i}',
            slug=f'accessories-product-{i}',
            description=f'accessories description {i}',
            price=f'{3000 + i * 100}',
            category=category_object_accessories
        ))
    return products


# empty database instance for every test
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass