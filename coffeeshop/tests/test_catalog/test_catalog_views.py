import pytest
from django.urls import reverse
from django.test import Client
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView
from django_filters.views import FilterView
from django.http import Http404

from catalog.models import Product, Category
from catalog.templatetags.catalog_tags import show_categories
from catalog.views import CoffeShopHome, CoffeShopCategory, ShowItem
from catalog.filters import ProductFilter
from catalog.utils import DataMixin


# UNIT tests

# CoffeShopHome queryset methods test
def test_coffe_shop_home_view_get_queryset():
    view = CoffeShopHome()
    queryset = view.get_queryset()
    assert queryset.model == Product
    assert queryset.ordered

# CoffeShopCategory queryset methods test
def test_coffe_shop_category_view_get_queryset(category_object_tea, product_object_tea):
    view = CoffeShopCategory()
    view.kwargs = {'category_slug': 'tea'}
    queryset = view.get_queryset()
    assert queryset.count() == 1
    assert queryset.first().category == category_object_tea

# ShowItem get_context_data methods test
def test_show_item_view_get_context_data(product_object_tea):
    view = ShowItem()
    view.object = product_object_tea
    context = view.get_context_data()
    assert context['title'] == f'{product_object_tea.category} - {product_object_tea.name}'


# INTEGRATION Tests

# home view test
def test_home_view(client, multiple_products):
    url = reverse('home')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'catalog.html' in [t.name for t in response.templates]
    assert 'cof_products' in response.context
    assert len(response.context['cof_products']) == 2  # main page pagination
    assert response.context['title'] == 'Catalog'
    assert 'filter' in response.context  # check filter exists in context


# catalog view test
def test_catalog_view(client, multiple_products):
    url = reverse('catalog')
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'catalog.html' in [t.name for t in response.templates]
    assert 'cof_products' in response.context
    assert len(response.context['cof_products']) == 2


# category view test
def test_category_view(client, category_object_tea, product_object_tea):
    url = reverse('category', kwargs={'category_slug': 'tea'})
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'catalog.html' in [t.name for t in response.templates]
    assert 'cof_products' in response.context
    assert response.context['title'] == 'Product category - TEA'
    assert all(p.category == category_object_tea for p in response.context['cof_products'])


# item view test
def test_item_view(client, product_object_tea):
    url = reverse('item', kwargs={'slug': 'test-product-1'})
    response = client.get(url)
    
    assert response.status_code == 200
    assert 'item.html' in [t.name for t in response.templates]
    assert 'item' in response.context
    assert response.context['item'] == product_object_tea
    assert response.context['title'] == f'{product_object_tea.category} - {product_object_tea.name}'


# no item test
def test_no_item(client):
    url = reverse('item', kwargs={'slug': 'nonexistent'})
    response = client.get(url)
    assert response.status_code == 404


# no category test
def test_nonexistent_category(client):
    url = reverse('category', kwargs={'category_slug': 'nonexistent'})
    response = client.get(url)
    assert response.status_code == 200  # we must have empty page
    assert 'catalog.html' in [t.name for t in response.templates]
    assert 'cof_products' in response.context
    assert len(response.context['cof_products']) == 0  # because we have empty product list
    assert response.context['title'] == 'Category not found'


# filtration test
def test_filter_products(client, multiple_products, sort_object):
    url = reverse('catalog')
    response = client.get(url, {'sort': sort_object.id}) # sort filtration
    
    assert response.status_code == 200
    assert 'cof_products' in response.context
    assert all(p.sort == sort_object for p in response.context['cof_products'])


# pagination test
def test_pagination(client, multiple_products):
    url = reverse('catalog')
    response = client.get(url)

    # default page
    assert response.status_code == 200
    assert 'cof_products' in response.context
    assert len(response.context['cof_products']) == 2
    
    # second page
    response = client.get(url, {'page': 2})
    assert response.status_code == 200
    assert len(response.context['cof_products']) == 2


# MOCK tests ================================================================

def test_home_view_db_interaction(monkeypatch, client, product_with_all_relations):
    def mock_all():
        return Product.objects.filter(pk=product_with_all_relations.pk)
    monkeypatch.setattr(Product.objects, 'all', mock_all)
    
    response = client.get(reverse('home'))
    assert response.status_code == 200
    assert response.context['title'] == 'Catalog'

def test_category_view_db_interaction(monkeypatch, client):
    def mock_filter(*args, **kwargs):
        return []
    monkeypatch.setattr(Product.objects, 'filter', mock_filter)
    
    response = client.get(reverse('category', kwargs={'category_slug': 'coffee'}))
    assert response.status_code == 200
    assert response.context['title'] == 'Category not found'

def test_show_item_view_db_interaction(monkeypatch, client):
    def mock_get(*args, **kwargs):
        raise Product.DoesNotExist()
    monkeypatch.setattr(Product.objects, 'get', mock_get)
    
    response = client.get(reverse('item', kwargs={'slug': 'test-coffee'}))
    assert response.status_code == 404


