#from django.contrib import admin
from django.urls import re_path, path, include

from .views import *
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

routerAdmin = routers.SimpleRouter()
routerAdmin.register(r'crudAdminProducts', AdminProductsSet, basename='crudAdminProducts')


urlpatterns = [
    path('api/signup/', RegisterUser.as_view(), name='registrate'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    #вход по соц сетям
    #восстановление пароля
    path('api/user/', UserView.as_view(), name='user'),
    path('api/user/update/', UserUpdateView.as_view(), name='user_update'),
    path('api/user/logout/', LogoutView.as_view(), name='logout'),
    path('api/catalogCats/', CatalogCatList.as_view(), name="categories"), #получить категории get
    path('api/catalogAll/', CatalogProductsList.as_view(), name="cat_all_products"), #получить все товары get
    path('api/catalog/<int:cat_id>/', CatalogOneCatList.as_view(), name="cat_id"), #получить товары по категориям get
    path('api/catalog/<slug:slug>/', ProductList.as_view(), name="product"), #получить 1 товар get
    path('api/trash/', TrashGetView.as_view(), name="trash"), #get корзину
    path('api/trashAdd/', TrashAddView.as_view(), name="trashAdd"), #создать запись в корзине post
    path('api/trashDelete/<int:pk>/', TrashDeleteView.as_view(), name="trashDelete"), #удалить запись в корзине delete
    path('api/likedAdd/', LikedAddView.as_view(), name="likedAdd"), #добавить в избранное post
    path('api/liked/', LikedGetView.as_view(), name="liked"), #get избранное
    path('api/likedDelete/<int:pk>/', LikedDeleteView.as_view(), name="likedDelete"), #удалить запись в избранномИстр delete
    path('api/', include(routerAdmin.urls), name="crud_product"), #CRUD products for admin create get put delete http://localhost:8000/api/crudAdminProducts/ - create prod read all prods http://localhost:8000/api/crudAdminProducts/slug - CRUD one prod
]
