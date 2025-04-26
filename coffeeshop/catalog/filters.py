from django_filters import FilterSet, filters

from .models import Product, Sort, Type, Region, Manufacture


class ProductFilter(FilterSet):

    sort = filters.ModelChoiceFilter(
        queryset=Sort.objects.filter(sorts__sort__isnull=False).distinct(),
        empty_label='Sort not chosen',
        label='Sort')

    type = filters.ModelChoiceFilter(
        queryset=Type.objects.filter(types__type__isnull=False).distinct(),
        empty_label='Type not chosen',
        label='Type')

    region = filters.ModelChoiceFilter(
        queryset=Region.objects.filter(regions__region__isnull=False).distinct(),
        empty_label='Region not chosen',
        label='Region')

    manufacture = filters.ModelChoiceFilter(
        queryset=Manufacture.objects.filter(manufacturers__manufacture__isnull=False).distinct(),
        empty_label='Manufacture not chosen',
        label='Manufacture')

    class Meta:
        model = Product
        fields = ['sort', 'type', 'region', 'manufacture']