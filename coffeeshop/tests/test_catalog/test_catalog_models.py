import pytest
from django.core.exceptions import ValidationError

from catalog.models import Product, Category, Sort, Type, Region, Manufacture


def test_empty_db():
    assert Product.objects.count() == 0


def test_full_db(product_object_tea):
    assert Product.objects.count() == 1


def test_product_db(product_object_tea):
    assert Product.objects.all()[0].name == 'test_product_1'
    assert Product.objects.all()[0].price == 1000.00


def test_product_invalid_name(product_null_name_object):
    with pytest.raises(ValidationError):
        product_null_name_object.full_clean()


def test_product_long_name(product_long_name_object):
    with pytest.raises(ValidationError):
        product_long_name_object.full_clean()


def test_product_duplicate_slug(product_duplicate_slug_object):
    with pytest.raises(ValidationError):
        product_duplicate_slug_object.full_clean()


def test_product_with_all_relations(product_with_all_relations):
    assert product_with_all_relations.name == 'full_product'
    assert product_with_all_relations.sort.name == 'Arabica'
    assert product_with_all_relations.type.name == 'Green'
    assert product_with_all_relations.region.name == 'Ethiopia'
    assert product_with_all_relations.manufacture.name == 'Lavazza'


def test_category_db(category_object_tea):
    assert category_object_tea.name == 'TEA'
    assert category_object_tea.slug == 'tea'
    assert category_object_tea.get_absolute_url() == '/catalog/tea/'


def test_category_invalid_name(category_null_name_object):
    with pytest.raises(ValidationError):
        category_null_name_object.full_clean()


def test_category_long_name(category_long_name_object):
    with pytest.raises(ValidationError):
        category_long_name_object.full_clean()


def test_category_duplicate_slug(category_duplicate_slug_object):
    with pytest.raises(ValidationError):
        category_duplicate_slug_object.full_clean()


def test_sort_db(sort_object):
    assert sort_object.name == 'Arabica'
    assert sort_object.slug == 'arabica'


def test_type_db(type_object):
    assert type_object.name == 'Green'
    assert type_object.slug == 'green'


def test_region_db(region_object):
    assert region_object.name == 'Ethiopia'
    assert region_object.slug == 'ethiopia'


def test_manufacture_db(manufacture_object):
    assert manufacture_object.name == 'Lavazza'
    assert manufacture_object.slug == 'lavazza'


def test_product_ordering(product_object_tea, product_with_all_relations):
    products = Product.objects.all()
    assert products[0].name == 'full_product'  # 'f' comes before 't'
    assert products[1].name == 'test_product_1'


def test_product_str(product_object_tea):
    assert str(product_object_tea) == 'test_product_1'


def test_category_str(category_object_tea):
    assert str(category_object_tea) == 'TEA'


def test_sort_str(sort_object):
    assert str(sort_object) == 'Arabica'


def test_type_str(type_object):
    assert str(type_object) == 'Green'


def test_region_str(region_object):
    assert str(region_object) == 'Ethiopia'


def test_manufacture_str(manufacture_object):
    assert str(manufacture_object) == 'Lavazza'
