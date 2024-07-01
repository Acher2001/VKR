from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('', views.city_list, name='city_list'),
    path('products/', views.product_list, name='product_list'),
    path('check/', views.form_check, name='check')
]
