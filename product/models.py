from django.db import models

class City(models.Model):
    name = models.CharField(max_length=250,
                            unique=True)

    class Meta:
        verbose_name_plural = 'Cities'

class Category(models.Model):
    name = models.CharField(max_length=250,
                            unique=True)
    class Meta:
        verbose_name_plural = 'Categories'

class Shop(models.Model):
    name = models.CharField(max_length=250)
    city = models.ForeignKey(City,
                    on_delete=models.CASCADE,
                    related_name='shops')
    website = models.CharField(max_length=250,
                               blank=True, null=True)
    address = models.CharField(max_length=250,
                               blank=True, null=True)

class Product(models.Model):
    name = models.CharField(max_length=250)
    number = models.IntegerField()
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name='products')
    shop = models.ForeignKey(Shop,
                    on_delete=models.CASCADE,
                    related_name='products')
    price = models.CharField(max_length=100,
                            blank=True, null=True)
    product_link = models.CharField(max_length=250,
                                    blank=True, null=True)
    image = models.CharField(max_length=255,
                              blank=True,
                              null=True)
