from django.contrib import admin

from catalog.models import Product, ProductCategory


admin.site.site_header = "Coffeeshop website administration panel"
admin.site.index_title = "Coffeeshop administration panel"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "description")
    list_display_links = ("name", "category")
    search_fields = ["name", "category__name"]
    list_filter = ["category__name", "sort", "product_type", "region", "manufacture"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}