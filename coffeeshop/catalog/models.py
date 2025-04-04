from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    image = models.ImageField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.ForeignKey('Category',
                                 on_delete=models.PROTECT,
                                 related_name='cats')
    sort = models.ForeignKey('Sort',
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name='sorts')
    type = models.ForeignKey('Type',
                             on_delete=models.SET_NULL,
                             null=True,
                             related_name='types')
    region = models.ForeignKey('Region',
                               on_delete=models.SET_NULL,
                               null=True,
                               related_name='regions')
    manufacture = models.ForeignKey('Manufacture',
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    related_name='manufacturers')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Sort(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Manufacture(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name
