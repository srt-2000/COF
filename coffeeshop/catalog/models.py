from django.db import models

class Product(models.Model):
    name = models.CharField()
    slug = models.SlugField()
    image = models.ImageField()
    description = models.TextField()
    price = models.DecimalField()

    # sort = models.ForeignKey()
    # type = models.ForeignKey()
    # category = models.ForeignKey()
    # region = models.ForeignKey()
    # manufacture = models.ForeignKey()

