from django.contrib import admin
from .models import City, Shop, Product, Category

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ['name',]
    list_display = ['id', 'name', ]

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    search_fields = ['name', 'address', ]
    list_display = ['name', 'address', ]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_display = ['name', 'number', 'price', ]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]
