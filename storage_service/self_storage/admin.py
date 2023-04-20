from django.contrib import admin

from .models import Box, Order, Size, Warehouse


admin.site.register(Box)
admin.site.register(Order)
admin.site.register(Size)
admin.site.register(Warehouse)
