from django.urls import path
from . import views

urlpatterns = [
    path(
        '',
        views.CoffeShopHome.as_view(),
        name='home'
    ),  # http://127.0.0.1:8000

    path(
        'catalog/',
        views.CoffeShopHome.as_view(),
        name='catalog'
    ),  # http://127.0.0.1:8000/catalog

    path(
        'catalog/<slug:category_slug>/',
        views.CoffeShopCategory.as_view(),
        name='category'
    ),  # http://127.0.0.1:8000/catalog/category_slug

    path(
        'catalog/item/<slug:slug>/',
        views.ShowItem.as_view(),
        name='item'
    ),  # http://127.0.0.1:8000/catalog/item

    path(
        'about/',
        views.CoffeShopHome.as_view(),
        name='about'
    ),  # http://127.0.0.1:8000/about

    path(
        'contact/',
        views.CoffeShopHome.as_view(),
        name='contact'
    ),  # http://127.0.0.1:8000/contact


]
