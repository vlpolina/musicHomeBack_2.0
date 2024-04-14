from django.contrib import admin
from .models import *


class ProdAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'count', 'time_update', 'is_published')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'short_desc')
    list_editable = ('is_published', )
    list_filter = ('is_published', 'time_update')
    prepopulated_fields = {"slug": ("name",)}


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'contacts')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'contacts', 'address')


class OrdersAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'ID_client')
    list_display_links = ('id', 'date')
    search_fields = ('id', 'date', 'ID_client')
    list_filter = ('date', )


class DeliveriesAdmin(admin.ModelAdmin):
    list_display = ('date', 'id', 'count')
    list_display_links = ('id', 'date')
    search_fields = ('id', 'date', 'ID_customer', 'ID_product')
    list_filter = ('date', )


class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Products, ProdAdmin)
admin.site.register(Customers, CustomerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(CostChange)
admin.site.register(Deliveries, DeliveriesAdmin)
