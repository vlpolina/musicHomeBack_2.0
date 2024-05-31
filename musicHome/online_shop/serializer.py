from rest_framework import serializers
from django.conf import settings
from .models import *
from django.contrib.auth.models import User
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'last_name', 'first_name']


class CheckAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_superuser', 'is_staff']


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Проверка на существование пользователя по электронной почте или имени пользователя
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с таким адресом электронной почты уже существует'})
        if User.objects.filter(username__iexact=validated_data['username']).exists():
            raise serializers.ValidationError({'username': 'Пользователь с таким username уже существует'})

        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user


class ProductCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'slug', 'name', 'short_desc', 'cost', 'count', 'photo', 'cat_id', 'custom_name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'slug', 'name', 'long_desc', 'short_desc', 'cost', 'count', 'photo', 'cat_id', 'custom_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class CustomersForCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = ['id', 'name']


class TrashSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = date.today()
    in_trash = serializers.HiddenField(default=1)

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'count', 'sum_cost', 'in_trash']


class OrderSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = date.today()
    in_trash = serializers.HiddenField(default=1)

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'count', 'sum_cost', 'in_trash', 'is_applying', 'phone', 'address', 'payment']


class CreatedOrdersSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = date.today()
    in_trash = serializers.HiddenField(default=1)

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'count', 'sum_cost', 'is_applying', 'is_payed', 'is_delivering', 'is_delivered', 'address', 'payment']


class LikedSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    date = date.today()
    in_liked = serializers.HiddenField(default=1)

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'count', 'sum_cost', 'in_liked']


class ProductCardSerializer(serializers.ModelSerializer):
    ID_client = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Orders
        fields = ['id', 'ID_client', 'ID_product', 'in_liked', 'in_trash']


class AdminProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"
