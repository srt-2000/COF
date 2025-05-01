from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


def empty_validator(value: str) -> None:
    """
    Validates that the value is not empty.

    Args:
        value: The string value to validate

    Raises:
        ValidationError: If the value is empty
    """
    if not value:
        raise ValidationError('This field can"t be empty')


class Product(models.Model):
    """
    Model representing a product in the coffee shop.

    Attributes:
        name: Product name
        slug: Unique URL-friendly identifier
        image: Product image
        description: Detailed product description
        price: Product price
        category: Product category
        sort: Product sort
        product_type: Product type
        region: Product region
        manufacture: Product manufacturer
    """

    objects = models.Manager()
    name = models.CharField(max_length=250, null=False, validators=[empty_validator])
    slug = models.SlugField(max_length=250, unique=True, null=False)
    image = models.ImageField(upload_to="photos/%Y/%m/%d/", default=None, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    category = models.ForeignKey("ProductCategory", on_delete=models.PROTECT, related_name="cats")
    sort = models.ForeignKey(
        "ProductSort", on_delete=models.SET_NULL, default=None, blank=True, null=True, related_name="sorts"
    )
    product_type = models.ForeignKey(
        "ProductType", on_delete=models.SET_NULL, default=None, blank=True, null=True, related_name="types"
    )
    region = models.ForeignKey(
        "ProductRegion", on_delete=models.SET_NULL, default=None, blank=True, null=True, related_name="regions"
    )
    manufacture = models.ForeignKey(
        "ProductManufacture", on_delete=models.SET_NULL, default=None, blank=True, null=True, related_name="manufacturers"
    )

    class Meta:
        verbose_name = "Products"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ProductCategory(models.Model):
    """
    Model representing a product category.

    Attributes:
        name: Category name
        slug: Unique URL-friendly identifier
    """

    objects = models.Manager()
    name = models.CharField(max_length=100, null=False, validators=[empty_validator])
    slug = models.SlugField(max_length=255, unique=True, null=False)

    def get_absolute_url(self) -> str:
        """
        Returns the absolute URL for the category.

        Returns:
            str: The URL for the category
        """
        return reverse("category", kwargs={"category_slug": self.slug})

    def __str__(self) -> str:
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


class ProductSort(AuxFieldModel):
    """
    Model representing a product sort.

    Attributes:
        name: Sort name
        slug: Unique URL-friendly identifier
    """

    pass


class ProductType(AuxFieldModel):
    """
    Model representing a product type.

    Attributes:
        name: Type name
        slug: Unique URL-friendly identifier
    """

    pass


class ProductRegion(AuxFieldModel):
    """
    Model representing a product region.

    Attributes:
        name: Region name
        slug: Unique URL-friendly identifier
    """

    pass


class ProductManufacture(AuxFieldModel):
    """
    Model representing a product manufacturer.

    Attributes:
        name: Manufacturer name
        slug: Unique URL-friendly identifier
    """

    pass
