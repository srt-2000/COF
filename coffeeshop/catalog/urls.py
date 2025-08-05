from __future__ import annotations

from django.urls import path

from catalog import views

urlpatterns = [
    path("", views.CoffeShopHome.as_view(), name="home"),
    path("catalog/", views.CoffeShopHome.as_view(), name="catalog"),
    path("catalog/<slug:category_slug>/", views.CoffeShopCategory.as_view(), name="category"),
    path("catalog/item/<slug:slug>/", views.ShowItem.as_view(), name="item"),
    path("about/", views.CoffeShopHome.as_view(), name="about"),
    path("contact/", views.CoffeShopHome.as_view(), name="contact"),
]
