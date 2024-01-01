from django.contrib import admin
from .models import Product, Order, Category, Customer
# Register your models here.
models = Product, Order, Category, Customer
for i in models:
    admin.site.register(i)
