from django import template

from catalog.models import Category

# from coffeeshop.catalog.utils import main_menu

from catalog.utils import main_menu

register = template.Library()

@register.simple_tag()
def get_main_menu():
    return main_menu


@register.inclusion_tag('list_categories.html')
def show_categories():
    cats = Category.objects.all()
    return {'cats': cats}
