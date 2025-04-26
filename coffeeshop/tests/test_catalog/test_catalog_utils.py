import pytest
from django.urls import reverse
from django.test import Client

from catalog.models import Product, Category
from catalog.utils import DataMixin


@pytest.mark.django_db
class TestDataMixin:
    # first page pagination test
    def test_pagination_default_page(self, client, multiple_products):
        url = reverse('catalog')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'cof_products' in response.context
        assert len(response.context['cof_products']) == 2  # paginate_by = 2
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 1
        assert response.context['page_obj'].has_next()
        assert not response.context['page_obj'].has_previous()

    # second page pagination test
    def test_pagination_second_page(self, client, multiple_products):
        url = reverse('catalog')
        response = client.get(url, {'page': 2})
        
        assert response.status_code == 200
        assert 'cof_products' in response.context
        assert len(response.context['cof_products']) == 2
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 2
        assert response.context['page_obj'].has_next()
        assert response.context['page_obj'].has_previous()

    # last page pagination test
    def test_pagination_last_page(self, client, multiple_products):
        url = reverse('catalog')
        response = client.get(url, {'page': 5})
        
        assert response.status_code == 200
        assert 'cof_products' in response.context
        assert len(response.context['cof_products']) == 1  # we have 1 product object on the last page
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 5
        assert not response.context['page_obj'].has_next()
        assert response.context['page_obj'].has_previous()

    # no page pagination test
    def test_pagination_invalid_page(self, client, multiple_products):
        url = reverse('catalog')
        response = client.get(url, {'page': 999})
        
        assert response.status_code == 404

    # empty page pagination test
    def test_pagination_empty_page(self, client):
        url = reverse('catalog')
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'cof_products' in response.context
        assert len(response.context['cof_products']) == 0
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 1
        assert not response.context['page_obj'].has_next()
        assert not response.context['page_obj'].has_previous()

    # category pages pagination test
    def test_pagination_category_view(self, client, category_object_tea, multiple_products):
        url = reverse('category', kwargs={'category_slug': 'tea'})
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'cof_products' in response.context
        assert len(response.context['cof_products']) == 2
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 1
        assert response.context['page_obj'].has_next()
        assert not response.context['page_obj'].has_previous()

    # filtered pages pagination test
    def test_pagination_with_filter(self, client, multiple_products, sort_object):
        # update the same sort field for every object
        for product in multiple_products:
            product.sort = sort_object
            product.save()
            
        url = reverse('catalog')
        response = client.get(url, {'sort': sort_object.id})
        
        assert response.status_code == 200
        assert 'cof_products' in response.context
        assert len(response.context['cof_products']) == 2
        assert 'page_obj' in response.context
        assert response.context['page_obj'].number == 1
        assert all(p.sort == sort_object for p in response.context['cof_products'])
