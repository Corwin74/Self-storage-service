from django.contrib import admin

from .models import Box, Order, Size, Warehouse


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'size')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'box')


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_size_value')

    @admin.display(description='Объем бокса')
    def get_size_value(self, obj):
        return obj.name
