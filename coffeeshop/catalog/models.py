from django.db import models


class Product(models.Model):
    """Product model (coffee/tea/accessories).
    
    Stores main product information including name, image,
    description, price and relationships with other models (category, sort, type etc.).
    """
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
    """Product category model.
    
    Defines product category (e.g.: coffee, tea, accessories).
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class AuxFieldModel(models.Model):
    """Abstract base model for auxiliary product models.
    
    Contains common fields for auxiliary models like Sort, Type, Region, Manufacture.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Sort(AuxFieldModel):
    """Product sort model.
    
    Defines coffee or tea sort (e.g.: arabica, robusta).
    """
    pass


class Type(AuxFieldModel):
    """Product type model.
    
    Defines accessories product type (e.g.: dishes, manual espresso).
    """
    pass


class Region(AuxFieldModel):
    """Origin product region model.
    
    Defines product origin region for tea/coffee (e.g.: Ethiopia, Brazil).
    """
    pass


class Manufacture(AuxFieldModel):
    """Manufacturer model.
    
    Defines product manufacturer foe accessories (e.g.: Philips, Sony).
    """
    pass
