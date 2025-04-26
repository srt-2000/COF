from django.views.generic import ListView, DetailView
from django_filters.views import FilterView

from .filters import ProductFilter
from .models import Product
from .utils import DataMixin


class CoffeShopHome(DataMixin, FilterView):
    model = Product  # name of model = get_queryset with return Project.objects.all()
    filterset_class = ProductFilter  # name of filter
    template_name = 'catalog.html'  # name of the template
    context_object_name = 'cof_products'  # name of template object_list
    extra_context = {'title': 'Catalog'}


class CoffeShopCategory(DataMixin, ListView):
    model = Product
    template_name = 'catalog.html'
    context_object_name = 'cof_products'

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs['category_slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['cof_products']:
            category_object = context['cof_products'][0].category
            context['title'] = 'Product category - ' + category_object.name
        else:
            context['title'] = 'Category not found'
        return context


class ShowItem(DetailView):
    model = Product
    template_name = 'item.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.category} - {self.object.name}'  # self.object - it's a current object of Product
        return context