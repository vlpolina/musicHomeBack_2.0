#from django.contrib import admin
from django.urls import re_path, path, include

from .views import *


urlpatterns = [
    path('catalog/', CatalogView.as_view(), name="cat"),
    path('catalog/all', CatalogViewAll.as_view(), name="cat_all"),
    path('catalog/filter_customers', FilterCustomersView.as_view(), name="filter_customers"),
    path('catalog/<int:cat_id>', CatalogViewID.as_view(), name="cat_id"),
    path('catalog/<slug:slug>', ProductView.as_view(), name="product"),
    path('trash/', TrashView.as_view(), name="trash"),
  #  path('trash/<int:pk>/', TrashDetailView.as_view(), name='trash-detail'),
    #path('login/', LoginUser.as_view(), name='log_in'),
    path('registrate/', RegisterUser.as_view(), name='registrate'),
]
