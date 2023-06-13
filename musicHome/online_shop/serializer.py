from rest_framework import serializers
from django.conf import settings
from .models import *
from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'short_desc', 'long_desc', 'cost', 'count', 'custom_name', 'photo', 'cat_id']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class FilterCustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id', 'name']


class TrashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'sum_cost']
