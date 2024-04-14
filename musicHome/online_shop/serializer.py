from rest_framework import serializers
from django.conf import settings
from .models import *
from django.contrib.auth.models import User
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'last_name', 'first_name']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class ProductCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'slug', 'name', 'short_desc', 'cost', 'count', 'photo', 'cat_id']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'slug', 'name', 'long_desc', 'cost', 'count', 'photo', 'cat_id', 'custom_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TrashSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = date.today()
    in_trash = serializers.HiddenField(default=1)

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'count', 'sum_cost', 'in_trash']


class LikedSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = date.today()
    in_liked = serializers.HiddenField(default=1)

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'count', 'sum_cost', 'in_liked']


class AdminProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"
